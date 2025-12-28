from rag_pipeline_agent.data.cleaning import cleaning_normalization
from rag_pipeline_agent.data.common.helpers import create_and_get_website_dir_if_not_exist, clean_up
from rag_pipeline_agent.data.crawling import crawl_helper
from rag_pipeline_agent.data.db import db_pipeline
from rag_pipeline_agent.data.q_a_generation import generate

choice = int(input("""
Please choose from the options below:
1. scrape a website and use it for retrieval augmented generation
2. use existing data for retrieval
"""))

if choice == 1:
    website_to_scrape = input("Please enter the website to scrape (e.g. https://www.google.com): ")
    # ill do checks for the url automatically
    website_name, website_path, file_path = create_and_get_website_dir_if_not_exist(website_to_scrape)

    print(50 * "/", "STEP 1: SCRAPPING", 50 * "/")
    crawl_helper.main(file_path, website_to_scrape)

    print(50*"/","STEP 2: DATA CLEANING", 50*"/")
    # let's clean the data now
    cleaning_normalization.main(file_path)

    print(50*"/","STEP 3: Q/A GENERATION", 50*"/")
    generate.main(file_path)

    print(50*"/","STEP 4: MONGO & VECTOR DB & EMBEDDINGS", 50*"/")
    db_pipeline.main(file_path, website_name, f"{website_path}_collection")

    # final clean_up
    clean_up("data/common/scrapped")
    print(50*"/","✅DONE✅", 50*"/")

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
            db_pipeline.query_collection(query,website_name, f"{website_path}_collection")


    elif query_choice == 2:
        launch_agent = int(input("""
Launch Agent??
1. Yes
2. No
            """.strip()))
        # will do later
    else:
        print("Wrong choice. Exiting...")

elif choice == 2:
    pass

else:
    print("Wrong option, please try again.")
