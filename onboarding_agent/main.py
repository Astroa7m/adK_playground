"""
Plan:
1- prepare & clean input
    - remove useless, very short convo
    - normalize latin characters
    - clean extra spaces, new lines, duplicates,
    - etc

2- give convo for LLM for summarization in a form of structured output

3- chunk and embed result and store in vector db

4- give same convo for LLM to generate config and save them in mongo db

5- done
"""
import json
import os
import threading
import time
from typing import Optional

from dotenv import load_dotenv
from google import genai
from google.genai import Client
from google.genai import types
from google.genai.local_tokenizer import LocalTokenizer
from pymongo import MongoClient
from tqdm import tqdm

from onboarding_agent.db.db_pipeline import insert_conversation
from onboarding_agent.models import ConversationList, AgentConfig
from onboarding_agent.prompts import QA_CHAT_CONVERSATION_STRUCTURED_OUTPUT_PROMPT, \
    AGENT_CONFIG_STRUCTURED_OUTPUT_PROMPT

load_dotenv()
api_key = os.getenv("GOOGLE_API_KEY")
gemini_client: Optional[Client] = None
mongo_client: Optional[MongoClient] = None
IN_LIMIT = 1_048_576
_lock = threading.Lock()
local_tokenizer: Optional[LocalTokenizer] = None
tenant_id = "tenant1"

def count_token_locally(data):
    try:
        ensure_local_tokenizer_instance()
        tokens = local_tokenizer.count_tokens(data)
        return tokens.total_tokens
    except Exception as e:
        raise RuntimeError(f"Google API error during token count: {e}")


def ensure_local_tokenizer_instance():
    global local_tokenizer
    if local_tokenizer is None:
        with _lock:
            if local_tokenizer is None:
                local_tokenizer = LocalTokenizer('gemini-2.5-flash')


def ensure_gemini_client():
    global gemini_client
    if gemini_client is None:
        with _lock:
            if gemini_client is None:
                gemini_client = genai.Client(api_key=api_key)


def ensure_mongo_instance(host="localhost", port=27017):
    global mongo_client
    if mongo_client is None:
        with _lock:
            if mongo_client is None:
                try:
                    mongo_client = MongoClient(host=host, port=port)
                except Exception as e:
                    raise ConnectionError(f"Failed to connect to MongoDB: {e}")


def get_chats(batch_size=10000):
    """Just a simulation of getting the data from api, db, whatever"""
    ensure_mongo_instance()
    try:
        db = mongo_client['k_playground']
        collection = db['chat_logs']

        # the plan is:
        # get all the distinct conversation ids with the max timestamp in descending order (latest message for each conversation)
        # for each of these conversation ids, get all the messages for that conversation

        # this gets all the unique conversation ids sorted by desc
        # SELECT DISTINCT conversation_id, max(date_time) FROM train group by conversation_id order by max(date_time) DESC LIMIT 10;

        # WITH latest AS (
        #   SELECT DISTINCT conversation_id, max(date_time) AS latest_act
        #   FROM train
        #   GROUP BY conversation_id
        # )
        # SELECT t.*
        # FROM train t
        # JOIN latest l ON t.conversation_id = l.conversation_id
        # ORDER BY l.latest_act DESC, t.date_time limit 2000;

        aggregation = [
            # we first get the latest time per conversation
            {
                "$group": {
                    "_id": "$conversation_id",
                    # timestamp is the name of the date_time filed in our data
                    "max_date_time": {"$max": "$timestamp"},
                    "messages": {"$push": "$content"},
                }
            },
            # # we sort by maximum date_time
            {
                "$sort": {
                    "max_date_time": -1  # desc
                }
            },
            {
                "$project": {
                    "_id": 1,
                    "conversation_id": "$_id",
                    "messages": 1,
                }
            }
        ]

        return collection.aggregate(aggregation).batch_size(batch_size)
    except Exception as e:
        raise RuntimeError(f"Something happened while getting chat logs: {e}")


def generate_structured_output(schema, system_prompt, content, timeout=90):
    ensure_gemini_client()
    try:
        response = gemini_client.models.generate_content_stream(
            model="gemini-2.5-flash-lite",
            contents=str(content),
            config=types.GenerateContentConfig(
                system_instruction=system_prompt,
                response_mime_type="application/json",
                response_json_schema=schema
            )
        )

        final_data = ""

        for chunk in tqdm(response, desc="Streaming chunks", unit="chunk"):
            final_data += chunk.text

        data = json.loads(final_data)


        return data

    except json.JSONDecodeError as e:
        print(f"Skipping chunk: LLM returned invalid JSON. Error: {e}")
        print("Skipping bad chunk")
        with open("data/dump/failure_chats.json", "w", encoding="utf-8") as f:
            f.write(final_data)
    except Exception as e:
        print(f"Unexpected error during generation: {e}")
        print("Skipping CHA chunk")


def onboard_chats(content, ids, categories):
    json_output = generate_structured_output(schema=ConversationList.model_json_schema(),
                                             system_prompt=QA_CHAT_CONVERSATION_STRUCTURED_OUTPUT_PROMPT, content=(content, categories))

    with open("data/dump/agent_chats.json", "w", encoding="utf-8") as f:
        json.dump(json_output, f, ensure_ascii=False, indent=4)

    # # adding back id for references
    # summarized_with_ids = [{"original_conversation_id": ids[i], "conversations": json_output[i] } for i in range(len(json_output))]
    #
    # insert_conversation(summarized_with_ids, tenant_id)


def onboard_config(content):
    json_output = generate_structured_output(schema=AgentConfig.model_json_schema(),
                                             system_prompt=AGENT_CONFIG_STRUCTURED_OUTPUT_PROMPT,
                                             content=content)
    # db = mongo_client['k_playground']
    # collection = db['agent_config']
    #
    # # we get it later for now static
    # collection.insert_one({"tenant_id": tenant_id, "config": json_output})

    with open("data/dump/agent_config.json", "w", encoding="utf-8") as f:
        json.dump(json_output, f, ensure_ascii=False, indent=4)


def get_categories():
    with open("data/dump/agent_config.json", encoding="utf-8") as f:
        data = json.load(f)
    return data['categories']


def main():
    max_prompt_token = max(count_token_locally(AGENT_CONFIG_STRUCTURED_OUTPUT_PROMPT), count_token_locally(QA_CHAT_CONVERSATION_STRUCTURED_OUTPUT_PROMPT))
    total_tokens = max_prompt_token
    print(f"Prompt tokens: {total_tokens}")

    # this will contain conversation that doesn't exceed IN_LIMIT
    # will be passed for generation
    eligible_conversation_messages = []
    # keeping a separate lists for ids to reduce tokens and noise
    eligible_conversation_ids = []
    docs = get_chats()

    for doc in tqdm(docs, desc="Overall Progress (Chunks)", unit="chunk"):
        conversation_id = doc["conversation_id"]
        # flattening the messages into a list of string
        messages = [d['text'] for d in doc['messages']]

        # checking the current tokens
        new_tokens = count_token_locally(str(messages))

        if new_tokens + total_tokens > IN_LIMIT * 0.98:  # adding some margin for '[' ',' ']' etc
            # we return early without the new data, so we stick to the limit
            print(f"Token limit reached at of the conversations, breaking...")
            break

        # if not then we add the messages and the ids
        eligible_conversation_messages.append(messages)
        eligible_conversation_ids.append(conversation_id)
        # increasing tokens cuount
        total_tokens += new_tokens
        print(f"current total tokens: {total_tokens}")

    # if we break out the loop, then we can start generating
    # onboard_config(eligible_conversation_messages)
    # print("Done config")
    categories = get_categories()
    onboard_chats(eligible_conversation_messages, eligible_conversation_ids, categories)
    print("Done chats")

    # todo add back ids to the summarized messages for reference
    # todo add chats to to milvus and mongo, then add agent config to mongo
if __name__ == "__main__":
    main()

