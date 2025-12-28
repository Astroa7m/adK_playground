import threading
from typing import Optional

from pymongo import MongoClient

document_1 = {
    "_id": "1",
    "name": "Ahmed",
    "age": 24,
    "degree": "CS"
}
document_2 = {
    "_id": "2",
    "name": "Mohammed",
    "age": 20,
    "degree": "Civil Engineering"
}

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


def main(db_name, collection_name, data):
    """Create mongo database, and the provided collection name, and inserts id, text into it"""
    ensure_mongo_instnace()
    # well, mongo handles the absence of db or collection, no need to check
    try:
        db = client[db_name]
        collection = db[collection_name]

        collection.insert_many(data)
    except Exception as e:
        raise RuntimeError(f"Mongo DB Creation failed: {e}")


def get_by_id(ids, db_name, collection_name):
    ensure_mongo_instnace()
    try:
        db = client[db_name]
        collection = db[collection_name]

        docs = collection.find({"_id": {"$in":ids}})
        return docs
    except Exception as e:
        raise RuntimeError(f"Exception occurred while searching vector db: {e}")
