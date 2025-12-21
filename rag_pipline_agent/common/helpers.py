from google import genai
from dotenv import load_dotenv
import os

CONTEXT_WINDOW = 1_000_000
load_dotenv()
api_key = os.getenv("GOOGLE_API_KEY")
print("loaded", api_key)
def count_token(data):
    """
    alternative though api
    POST https://generativelanguage.googleapis.com/v1beta/models/*:countTokens
    {
    "contents": [{
        "parts": [{"text": [data]}] }]
    }
    """
    client = genai.Client(api_key=api_key)
    tokens = client.models.count_tokens(
        model='gemini-2.5-flash',
        contents=data,
    )
    return tokens

def check_context_availability():
    ### todo check if the data went out of context to chunk it
    pass

if __name__ == "__main__":
    data = input("Enter data to start counting: ")
    count = count_token(data).total_tokens
    print("count", count)
    print("You are only using:",count/CONTEXT_WINDOW*100, "of memory")
