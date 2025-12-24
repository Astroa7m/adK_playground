from rag_pipeline_agent.data.cleaning import cleaning_normalization
from rag_pipeline_agent.data.common.helpers import create_and_get_website_dir_if_not_exist
from rag_pipeline_agent.data.crawling import crawl_helper
from rag_pipeline_agent.data.q_a_generation import generate
from rag_pipeline_agent.data.vector_db import db_setup

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

    print(50*"/","STEP 4: VECTOR DB & EMBEDDINGS", 50*"/")
    db_setup.main(file_path, f"./{website_name}.db", f"{website_path}_collection")

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
            result = db_setup.query_collection(query, f"./{website_name}.db", f"{website_path}_collection")
            print(f"Result\n{result}")


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

