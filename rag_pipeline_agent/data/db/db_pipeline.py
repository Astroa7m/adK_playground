import json
import os
from pathlib import Path

from rag_pipeline_agent.data.common import Q_A_EXT
from rag_pipeline_agent.data.common.helpers import clean_up
from rag_pipeline_agent.data.db import milvus_client, mongo_client
from rag_pipeline_agent.data.embedding.embed import embed_and_get_result, embed


def query_collection(query: str, db_name, collection_name):
    try:
        # getting the first embeddings
        [result] = embed(query).embeddings

        # search in vector db and get the id

        ids = milvus_client.query(result, db_name, collection_name)
        print(f"retrieved docs from mongodb based on ids\n{ids}")
        # get the actual text from mongo bb based on the retrieved id

        retrieved_result = mongo_client.get_by_id(ids, db_name, collection_name)
        print(f"retrieved docs from mongodb based on ids")
        for row in retrieved_result:
            print(row)
    except Exception as e:
        raise RuntimeError(f"Querying DB collection failed: {e}")


def main(file_path, db_name, collection_name):
    in_file_path = file_path / Q_A_EXT

    if not os.path.exists(in_file_path):
        raise FileNotFoundError(f"Missing Q/A data at {in_file_path}")

    try:
        with open(in_file_path, encoding="utf-8") as f:
            qa = json.load(f)

            result = embed_and_get_result(qa)
            print(f"got all data from embedding with length {len(result)}")

            # insert ids and vectors only in milvus
            data_for_milvus = [
                {
                    "id": r['id'],
                    "vector": r["vector"]
                }
                for r in result]
            print(f"got data for milvus with length {len(data_for_milvus)}")
            milvus_client.main(db_name, collection_name, data_for_milvus)
            print("DONE INSERTING TO MILVUS")

            # insert ids and text into mongo
            data_for_mongo = [
                {
                "_id": r['id'],
                "text": r["text"]
                }
                for r in result]
            mongo_client.main(db_name, collection_name, data_for_mongo)
            print(f"got data for mongo with length {len(data_for_mongo)}")
            print("DONE INSERTING TO MONGO")

        clean_up(in_file_path)
    except Exception as e:
        raise RuntimeError(f"Something happened with the db operation: {e}")


if __name__ == "__main__":
    # main(Path(r"C:\Users\ahmed\PycharmProjects\tryingADK\rag_pipeline_agent\data\common\scrapped\omantel"), "omanteldb", "omantel_collection")
    query_collection("omantel service", "omanteldb", "omantel_collection")
