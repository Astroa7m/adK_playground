import json
import os
import threading
from typing import Optional

from dotenv import load_dotenv
from pymilvus import MilvusClient
from google import genai
from google.genai import types, Client

load_dotenv()

api_key = os.getenv("GOOGLE_API_KEY")
ZILLIZ_USER = os.getenv("ZILLIZ_USER")
ZILLIZ_PASSWORD = os.getenv("ZILLIZ_PASSWORD")
ZILLIZ_ENDPOINT = os.getenv("ZILLIZ_ENDPOINT")

DIMENSION_SIZE = 768
in_file_path = "../common/q_a.json"

gemini_client: Optional[Client] = None
milvus_client: Optional[MilvusClient] = None
_lock = threading.Lock()

def ensure_milvus_instance(db_name):
    global milvus_client
    if milvus_client is None:
        with _lock:
            if milvus_client is None:
                milvus_client = MilvusClient(
                    db_name=db_name,
                    uri=ZILLIZ_ENDPOINT,
                    token=f"{ZILLIZ_USER}:{ZILLIZ_PASSWORD}",
                )

def ensure_gemini_client():
    global gemini_client
    if gemini_client is None:
        with _lock:
            if gemini_client is None:
                gemini_client = genai.Client(api_key=api_key)


def create_vector_db(db_name: str, collection_name):
    ensure_milvus_instance(db_name)
    ensure_gemini_client()

    if milvus_client.has_collection(collection_name=collection_name):
        milvus_client.drop_collection(collection_name=collection_name)

    milvus_client.create_collection(
        collection_name=collection_name,
        dimension=DIMENSION_SIZE
    )

    with open(in_file_path, encoding="utf-8") as f:
        qa = json.load(f)

    result = gemini_client.models.embed_content(
        model="gemini-embedding-001",
        contents=qa,
        config=types.EmbedContentConfig(output_dimensionality=DIMENSION_SIZE)
    )
    data = [
        {"id": i, "vector": result.embeddings[i].values, "text": qa[i], "type": "qa"}
        for i in range(len(result.embeddings))
    ]

    res = milvus_client.insert(collection_name=collection_name, data=data)
    print(res)


def query_collection(db_name, query: str, collection_name: str):
    ensure_milvus_instance(db_name)
    ensure_gemini_client()

    [result] = gemini_client.models.embed_content(
        model="gemini-embedding-001",
        contents=query,
        config=types.EmbedContentConfig(output_dimensionality=DIMENSION_SIZE)
    ).embeddings

    res = milvus_client.search(
        collection_name=collection_name,
        data=[result.values],
        limit=8,
        output_fields=["text"],
    )
    text_result = [item['entity'] for item in res[0]]
    print(text_result)

if __name__ == "__main__":
    # create_vector_db("./test_vector.db", "test_collection_name")
    query_collection("./test_vector.db","Does Omantel have a 5g service?", "test_collection_name")