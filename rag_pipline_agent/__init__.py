from . import agent


"""
Plan:
- Prompt the user to choose either "upload data for retrieval" or use "existing retrieval"

"upload data for retrieval":
- take url from user
- send the url to firecrawl api to crawl and scrape it into markdown (>= 10 pages)
- clean the data if needed (normalization, removing weird characters, keeping english only, etc.) 
- send the data to LLM for QA json generation (whether splitting data, or send corpus)
- chunk the collected q/a docs json into qa pairs
- embed them using gemini embedding models
- insert embedded docs into melvis
- done

"existing retrieval"
- search in retrieval file for existing vector db or remotely in melvis
- if files > 1: show the user the choices to start retrieving, if files ==1, start retrieving, else go to choice 1 or exit 
- the LLM retrieval tool will have to query the vector db with 5 different queries and each will return 10 top k sorted
- merge the result, deduplicate and get the top 3 answers and provide it to the user
- loop if needed for extra questions
- done
"""