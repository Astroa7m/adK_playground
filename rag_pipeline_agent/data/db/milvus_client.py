import os
import threading
from typing import Optional

from dotenv import load_dotenv
from pymilvus import MilvusClient

from rag_pipeline_agent.data.common import DIMENSION_SIZE

load_dotenv()

ZILLIZ_USER = os.getenv("ZILLIZ_USER")
ZILLIZ_PASSWORD = os.getenv("ZILLIZ_PASSWORD")
ZILLIZ_ENDPOINT = os.getenv("ZILLIZ_ENDPOINT")

client: Optional[MilvusClient] = None
_lock = threading.Lock()


def ensure_milvus_instance(db_name):
    global client
    if client is None:
        with _lock:
            if client is None:
                try:
                    client = MilvusClient(
                        db_name=db_name,
                        uri=ZILLIZ_ENDPOINT,
                        token=f"{ZILLIZ_USER}:{ZILLIZ_PASSWORD}",
                    )
                except Exception as e:
                    raise ConnectionError(f"Failed to connect to Zilliz/Milvus: {e}")


def main(db_name, collection_name, data):
    """Create vector database, and the provided collection name, and inserts id, vector into it"""
    db_name =  db_name + ".db"
    ensure_milvus_instance(db_name)

    try:
        if client.has_collection(collection_name=collection_name):
            client.drop_collection(collection_name=collection_name)

        client.create_collection(
            collection_name=collection_name,
            dimension=DIMENSION_SIZE
        )

        res = client.insert(collection_name=collection_name, data=data)
        print(f"Data inserted Successfully: {res}")
    except Exception as e:
        raise RuntimeError(f"Vector DB Creation failed: {e}")


def query(embeddings, db_name, collection_name, limit=8):
    db_name = db_name + ".db"
    ensure_milvus_instance(db_name)

    try:
        res = client.search(
            collection_name=collection_name,
            data=[embeddings.values],
            limit=limit,
            output_fields=["id"],
        )[0]

        ids = [hit.get("id") or hit["entity"].get("id") for hit in res]
        return ids
    except Exception as e:
        raise RuntimeError(f"Exception occurred while searching vector db: {e}")


if __name__ == "__main__":
    # create_vector_db("./test_vector.db", "test_collection_name")
    pass
