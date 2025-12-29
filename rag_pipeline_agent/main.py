import json
import os
from pathlib import Path

from rag_pipeline_agent.data.cleaning import cleaning_normalization
from rag_pipeline_agent.data.common.helpers import create_and_get_website_dir_if_not_exist, clean_up
from rag_pipeline_agent.data.crawling import crawl_helper
from rag_pipeline_agent.data.q_a_generation import generate
from rag_pipeline_agent.db import db_pipeline

choice = int(input("""
Please choose from the options below:
1. scrape a website and use it for retrieval augmented generation
2. use existing data for retrieval
"""))


def launch_agent():
    tenants = db_pipeline.list_available_tenants()

    if tenants:
        q = ""
        for i, t in enumerate(tenants):
            q += f"{i + 1}. {t}\n"
        if q:
            try:
                chosen_tenant_index = int(input(f"Please choose one of the available tenants\n{q}")) - 1
                chosen_tenant = tenants[chosen_tenant_index]

                data = {
                    "tenant": chosen_tenant
                }

                with open("common/current_knowledge_config.json", "w") as f:
                    json.dump(data, f, ensure_ascii=False, indent=4)
            except Exception as e:
                print(f"Something went wrong: {e}")

    print("Calling the agent to serve you, please wait.")
    path_to_agent = Path(__file__).parents[1] / "rag_pipeline_agent"
    os.system(f"adk run {path_to_agent}")


if choice == 1:
    website_to_scrape = input("Please enter the website to scrape (e.g. https://www.google.com): ")
    # ill do checks for the url automatically
    website_name, website_path, file_path = create_and_get_website_dir_if_not_exist(website_to_scrape)

    print(50 * "/", "STEP 1: SCRAPPING", 50 * "/")
    crawl_helper.main(file_path, website_to_scrape)

    print(50 * "/", "STEP 2: DATA CLEANING", 50 * "/")
    # let's clean the data now
    cleaning_normalization.main(file_path)

    print(50 * "/", "STEP 3: Q/A GENERATION", 50 * "/")
    generate.main(file_path)

    print(50 * "/", "STEP 4: MONGO & VECTOR DB & EMBEDDINGS", 50 * "/")
    db_pipeline.main(file_path, website_name)

    # final clean_up
    clean_up("data/common/scrapped")
    print(50 * "/", "✅DONE✅", 50 * "/")

    query_choice = int(input("""
Would you like to query database before exit?
1. Yes
2. No
"""))

    if query_choice == 1:
        while True:
            query = input("Enter query (type 'exit' to finish): ")

            if query == "exit":
                break
            result = db_pipeline.query_knowledge_base(query, website_name)
            print(result)


    elif query_choice == 2:
        launch_agent_choice = int(input("""
Launch Agent??
1. Yes
2. No
            """.strip()))
        if launch_agent_choice == 1:
            launch_agent()
        else:
            print("Bye.")
    else:
        print("Wrong choice. Exiting...")

elif choice == 2:
    launch_agent()
else:
    print("Wrong option, please try again.")
