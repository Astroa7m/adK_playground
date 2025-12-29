import threading
from typing import Optional

from pymongo import MongoClient

from rag_pipeline_agent.common.constants import DB_NAME, COLLECTION_NAME

client: Optional[MongoClient] = None
_lock = threading.Lock()


def ensure_mongo_instnace(host="localhost", port=27017):
    global client
    if client is None:
        with _lock:
            if client is None:
                try:
                    client = MongoClient(host=host, port=port)
                except Exception as e:
                    raise ConnectionError(f"Failed to connect to MongoDB: {e}")


def main(data):
    """Create mongo database, and the provided collection name, and inserts id, text into it"""
    ensure_mongo_instnace()
    # well, mongo handles the absence of db or collection, no need to check
    try:
        db = client[DB_NAME]
        collection = db[COLLECTION_NAME]

        collection.insert_many(data)
    except Exception as e:
        raise RuntimeError(f"Mongo DB Creation failed: {e}")


def get_by_id(ids):
    ensure_mongo_instnace()
    try:
        db = client[DB_NAME]
        collection = db[COLLECTION_NAME]

        docs = collection.find({"_id": {"$in": ids}})
        return docs
    except Exception as e:
        raise RuntimeError(f"Exception occurred while searching vector db: {e}")


def list_tenants():
    ensure_mongo_instnace()
    db = client[DB_NAME]
    collection = db[COLLECTION_NAME]
    tenants = collection.distinct("tenant")
    return tenants
