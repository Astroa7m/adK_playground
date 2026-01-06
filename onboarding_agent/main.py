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
from pymongo import MongoClient
from tqdm import tqdm

load_dotenv()
api_key = os.getenv("GOOGLE_API_KEY")
gemini_client: Optional[Client] = None
mongo_client: Optional[MongoClient] = None

_lock = threading.Lock()


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


def get_chats():
    """Just a simulation of getting the data from api, db, whatever"""
    ensure_mongo_instance()
    try:
        db = mongo_client['orki_playground']
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
                    "messages": {"$push": "$$ROOT"}
                }
            },
            # we
            {
                "$sort": {
                    "max_date_time": -1  # desc
                }
            },
            {
                "$limit": 10
            }
        ]

        return collection.aggregate(aggregation)
    except Exception as e:
        raise RuntimeError(f"Something happened while getting chat logs: {e}")


def generate_structured_output(schema, system_prompt, content, timeout=30):
    ensure_gemini_client()
    start = time.time()
    try:
        response = gemini_client.models.generate_content_stream(
            model="gemini-2.5-flash-lite",
            contents=content,
            config=types.GenerateContentConfig(
                system_instruction=system_prompt,
                response_mime_type="application/json",
                response_json_schema=schema
            )
        )

        final_data = ""

        for chunk in tqdm(response, desc="Streaming chunks", unit="chunk"):
            if time.time() - start > timeout:
                print("Timeout reached for this chunk, skipping to next...")
                break  # stop this chunk, continue outer loop
            final_data += chunk.text

        data = json.loads(final_data)

        if not isinstance(data, list):
            raise ValueError("LLM did not return a list of Q/A pairs.")

        return data

    except json.JSONDecodeError as e:
        print(f"Skipping chunk: LLM returned invalid JSON. Error: {e}")
        print(f"Returned response: {data}")
        print("Skipping bad chunk")
    except Exception as e:
        print(f"Unexpected error during generation: {e}")
        print("Skipping bad chunk")


def onboard_chats():
    pass


def onboard_config():
    pass


if __name__ == "__main__":
    docs = get_chats()
    for row in docs:
        print(row)
