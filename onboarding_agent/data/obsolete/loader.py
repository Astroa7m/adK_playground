# with remote token calculation
# 23:37 mins for 10_000 chunk/rows and 631400 tokens # PASS 1
# 37:23 mins for 16_296 chunk/rows and 1025488 tokens # TOTAL PASS

"""
Plan for extended data and production of high quality convo:
- PII Redaction using NER (Microsoft Presidio or SpaCy)
- Flag low quality conversation
    -with agent-to-client ratio higher than some threshold to review manually
    -spamming of messages, time calculation against word per minute of each session
- Collapse multiple consecutive turns of same sender into one
- Remove noise:
    -short messages ("Hello" or emojis)
    -system message ("An agent will be with you shortly")
- Fix spelling with SymSpell or similar
- Exact-deduplicate and near-deduplicate
- Engagement filtering (unresolved conversations, or customer ditched conversation)
"""
import threading
import time
from datetime import datetime
from typing import Optional

from google.genai import Client
from google.genai.local_tokenizer import LocalTokenizer
from tqdm import tqdm

from onboarding_agent.prompts import SUMMARIZE_CHAT_CONVERSATION_STRUCTURED_OUTPUT_PROMPT

output_conversation_test_format = {
    "some_id": [
        {
            "sender": "sender",
            "timestamp": "timestamp",
            "message": "message"
        }
    ]
}

# we converted the csv to this for each message to make it easy for us to manipulate them in dump_conversations
# and checking for existence in output conversation
extra_conversation_test_format = [
    {
        "conversation_id": "2",
        "message": {
            "sender": "sender1",
            "timestamp": "1",
            "message": "message1"
        }
    }
]

"""
Summary of what have been accomplished here:
- iterated through the csv via chunk size to avoid loading the entire 5.5 M rows into RAM and to calculate the tokens so far so we stop before hitting the LLM max tokens
- converted the csv of convo chunk into the following format:
        test_data = {
                "some_id": [
                    {
                        "sender": "sender",
                        "timestamp": "timestamp",
                        "message": "message"
                    }
                ], ....
            }
            - each conversation id holds it corresponding messages
             to save tokens (instead of repeating conversation id or message object with the same id) 
            - messages objects are are added into message list with a sorted order asc by timestamp with O(n) insertion (insort with bisect and binary search) total O (n log n) for each
            - calculate tokens of each message and added them to the total calculation of the prompt
            - broke out once the limit of input tokens reached
"""
import json
import os
from bisect import insort

import pandas as pd
from dotenv import load_dotenv
from google import genai

load_dotenv()
COUNT_TOKEN_RPM_LIMIT = 3000
CHUNKSIZE = 10_000
IN_LIMIT = 1_048_576
OUT_LIMIT = 65_536
CONTEXT_WINDOW_LIMIT = IN_LIMIT + OUT_LIMIT
api_key = os.getenv("GOOGLE_API_KEY")
genai_client: Optional[Client] = None
_lock = threading.Lock()

local_tokenizer = LocalTokenizer('gemini-2.5-flash')
def ensure_genai_client():
    global genai_client
    if not api_key:
        raise KeyError("GOOGLE_API_KEY not found. Token counting impossible.")

    if genai_client is None:
        with _lock:
            if genai_client is None:
                genai_client = genai.Client(api_key=api_key)

def count_token(data):
    ensure_genai_client()
    """
    alternative though api
    POST https://generativelanguage.googleapis.com/v1beta/models/*:countTokens
    {
    "contents": [{
        "parts": [{"text": [data]}] }]
    }
    """

    try:
        tokens = genai_client.models.count_tokens(
            model='gemini-2.5-flash',
            contents=data,
        )
        return tokens.total_tokens
    except Exception as e:
        raise RuntimeError(f"Google API error during token count: {e}")
def count_token_locally(data):
    try:
        tokens = local_tokenizer.count_tokens(data)
        return tokens.total_tokens
    except Exception as e:
        raise RuntimeError(f"Google API error during token count: {e}")



def dump_conversations(out_file_path: str, extra_conversation: list):
    data = {}
    # checking if file exists and loading existing data
    if os.path.exists(out_file_path) and os.path.getsize(out_file_path) > 0:
        with open(out_file_path, "r", encoding="utf-8") as f:
            data = json.load(f)

    for conversation in extra_conversation:
        conversation_id = conversation["conversation_id"]
        message = conversation['message']
        if conversation_id in data:
            # adding the message in sorted order using bisect (uses binary search internally)
            # we are going to sort them by timestamp
            insort(data[conversation_id], message, key=lambda x: x['timestamp'])
        else:
            data[conversation_id] = [conversation['message']]

    with open(out_file_path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)


def load_conversation_by_chunks(used_prompt):
    total_tokens = count_token_locally(used_prompt)
    print(f"Prompt tokens: {total_tokens}")
    # original ds: https://huggingface.co/datasets/talkmap/banking-conversation-corpus/tree/main
    total_rows = sum(1 for _ in open("../dump/banking_300k.csv", 'r', encoding='utf-8')) - 1  # subtract 1 for header
    total_chunks = total_rows // CHUNKSIZE
    # using chunk size to return an iterator where every step (chunk) has n rows
    # so it's like have a lazy loader instead of loading all at once
    df = pd.read_csv("../dump/banking_300k.csv", chunksize=CHUNKSIZE)
    conversations = {}
    with tqdm(total=total_chunks, desc="Overall Progress (Chunks)", unit="chunk") as pbar_outer:
        for chunk in df:
            # this will return a Panda object containing the fields of each row
            # e.g. Pandas(Index=0, conversation_id='2b6544c382e6423b96785c1a135d8e95', speaker='agent', date_time='2023-09-06T14:33:33+00:00', text='Good morning, thank you for calling Union Financial. My name is Monroe, how can I assist you today?')
            for row in tqdm(chunk.itertuples(), total=len(chunk), desc="Processing Rows", leave=False):

                new_message = {
                    "sender": row.speaker,
                    "timestamp": row.date_time,
                    "message": row.text
                }


                # we check if the new message will make the conversations go beyond the input limit before appending it along with the prompt tokens
                new_tokens = count_token_locally(str(new_message))

                print(f"new tokens: {new_tokens}")

                if new_tokens + total_tokens > IN_LIMIT * 0.98:  # adding some margin for '[' ',' ']' etc
                    # we return early without the new data, so we stick to the limit
                    print(f"Token limit reached at of the conversations, returning the list")
                    return conversations

                total_tokens += new_tokens

                if row.conversation_id in conversations:
                    # adding the message in sorted order using bisect (uses binary search internally)
                    # we are going to sort them by timestamp

                    insort(conversations[row.conversation_id], new_message, key=lambda x: x['timestamp'])
                else:
                    conversations[row.conversation_id] = [new_message]

                print(f"total tokens so far: {total_tokens}")

    # if we reach here then the conversations are less than the input limit
    return conversations


if __name__ == "__main__":
    total_conversation = load_conversation_by_chunks(SUMMARIZE_CHAT_CONVERSATION_STRUCTURED_OUTPUT_PROMPT)
    # writing them to a file just for debugging
    with open("../dump/test2.json", "w", encoding="utf-8") as f:
        json.dump(total_conversation, f, ensure_ascii=False, indent=4)