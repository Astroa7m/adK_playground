import os
import threading
from typing import Optional

from dotenv import load_dotenv
from pymilvus import MilvusClient


load_dotenv()

ZILLIZ_USER = os.getenv("ZILLIZ_USER")
ZILLIZ_PASSWORD = os.getenv("ZILLIZ_PASSWORD")
ZILLIZ_ENDPOINT = os.getenv("ZILLIZ_ENDPOINT")

client: Optional[MilvusClient] = None
_lock = threading.Lock()

DB_NAME = "k_playground"

_DB_NAME = DB_NAME + ".db"
COLLECTION_NAME = "rag"
DIMENSION_SIZE = 768

def ensure_milvus_instance():
    global client
    if client is None:
        with _lock:
            if client is None:
                try:
                    client = MilvusClient(
                        db_name=_DB_NAME,
                        uri=ZILLIZ_ENDPOINT,
                        token=f"{ZILLIZ_USER}:{ZILLIZ_PASSWORD}",
                    )
                except Exception as e:
                    raise ConnectionError(f"Failed to connect to Zilliz/Milvus: {e}")


def main(data):
    """Create vector database, and the provided collection name, and inserts id, vector into it"""
    ensure_milvus_instance()

    try:
        # if client.has_collection(collection_name=COLLECTION_NAME):
        #    client.drop_collection(collection_name=COLLECTION_NAME)

        client.create_collection(
            collection_name=COLLECTION_NAME,
            dimension=DIMENSION_SIZE
        )

        res = client.insert(collection_name=COLLECTION_NAME, data=data)
        print(f"Data inserted Successfully: {res}")
    except Exception as e:
        raise RuntimeError(f"Vector DB Creation failed: {e}")


def query(embeddings, tenant_name, limit=3):
    ensure_milvus_instance()
    target_output_fields = ["tenant"]
    try:
        search_result = client.search(
            collection_name=COLLECTION_NAME,
            data=[embeddings.values],
            filter=f'tenant == "{tenant_name}"',
            limit=limit,
            output_fields=target_output_fields
        )[0]
        target_output = []
        for row_dict in search_result:
            # adding the default returns from the search result to our current dict
            current_row_dict = {
                "id": row_dict['id'],
                # this is cosine distance by default (the higher the better)
                "distance": row_dict['distance']
            }
            # flattening the 'entity' dict within every 'row_dict' in the search result
            for key in target_output_fields:
                current_row_dict[key] = row_dict['entity'][key]

            target_output.append(current_row_dict)
        return target_output
    except Exception as e:
        raise RuntimeError(f"Exception occurred while searching vector db: {e}")


def list_tenants():
    ensure_milvus_instance()

    results = client.query(
        COLLECTION_NAME,
        filter='',
        output_fields=['tenant'],
        # arbitrary, as if we have 1000 tenants
        limit=1000
    )

    tenants = list({r["tenant"] for r in results})

    return tenants


if __name__ == "__main__":
    print(list_tenants())
