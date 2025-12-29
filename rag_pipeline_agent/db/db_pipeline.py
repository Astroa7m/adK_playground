import json
import os

from rag_pipeline_agent.data.common.constants import Q_A_EXT
from rag_pipeline_agent.data.common.helpers import clean_up
from rag_pipeline_agent.db import milvus_client, mongo_client
from rag_pipeline_agent.embedding.embed import embed_and_get_result, embed


def query_knowledge_base(query: str, tenant_name):
    try:
        # getting the first embeddings
        [result] = embed(query).embeddings

        # search in vector db and get the id
        # sorting them by id
        milvus_retrieved_result = sorted(milvus_client.query(result, tenant_name), key=lambda x: x['id'])

        # get the actual text from mongo bb based on the retrieved id
        ids = [item["id"] for item in milvus_retrieved_result]
        # sorting them by id
        mongo_retrieved_result = sorted(mongo_client.get_by_id(ids), key=lambda x: x['_id'])

        # we want to retrieve a final list of ids, text, score (distance), and text
        # so we are going to combine result from both clietns
        final_output = []

        # now since both results are sorted based on ids we can add text from mongo result to
        # milvus dict with one loop to reduce complexity

        # quick check
        if len(mongo_retrieved_result) != len(milvus_retrieved_result):
            raise RuntimeError("Dbs' result lengths are not the same")

        # any length since both are same
        for i in range(len(mongo_retrieved_result)):
            current_milvus_row_dict = milvus_retrieved_result[i]
            current_text_for_dict = mongo_retrieved_result[i]['text']

            current_milvus_row_dict["text"] = current_text_for_dict

            final_output.append(current_milvus_row_dict)

        return final_output
    except Exception as e:
        raise RuntimeError(f"Querying DB collection failed: {e}")


def main(file_path, tenant):
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
                    "vector": r["vector"],
                    "tenant": tenant
                }
                for r in result]
            print(f"got data for milvus with length {len(data_for_milvus)}")
            milvus_client.main(data_for_milvus)
            print("DONE INSERTING TO MILVUS")

            # insert ids and text into mongo
            data_for_mongo = [
                {
                    "_id": r['id'],
                    "text": r["text"],
                    "tenant": tenant
                }
                for r in result]
            mongo_client.main(data_for_mongo)
            print(f"got data for mongo with length {len(data_for_mongo)}")
            print("DONE INSERTING TO MONGO")

        clean_up(in_file_path)
    except Exception as e:
        raise RuntimeError(f"Something happened with the db operation: {e}")


def list_available_tenants():
    # first let's list mongo collection
    try:
        mongo_tenants = sorted(mongo_client.list_tenants())
    except Exception as e:
        raise RuntimeError(f"Failed to fetch mongo tenants: {e}")

    # then we gonna list collections in mivlus
    try:
        milvus_tenants = sorted(milvus_client.list_tenants())
    except Exception as e:
        raise RuntimeError(f"Failed to fetch milvus tenants: {e}")

    if mongo_tenants != milvus_tenants:
        raise RuntimeError(
            f"Mongo tenants and Milvus tenants are invalidated\nMongo: {mongo_tenants}\nMilvus: {milvus_tenants}")

    # returning any of them
    return mongo_tenants


if __name__ == "__main__":
    # main(Path(r"C:\Users\ahmed\PycharmProjects\tryingADK\rag_pipeline_agent\data\common\scrapped\omantel"), "omanteldb", "omantel_collection")
    # query_collection("omantel service",  "omantel_collection")
    query_knowledge_base("working hours", "awasr")
