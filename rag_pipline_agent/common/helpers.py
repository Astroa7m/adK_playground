from google import genai
from dotenv import load_dotenv
import os

CONTEXT_WINDOW = 1_000_000
load_dotenv()
api_key = os.getenv("GOOGLE_API_KEY")
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
    return tokens.total_tokens

def chunk_by_context_window(data: list[str]) -> list[str]:
    """
    A recursive function that is going to check if the input is out of context window, to chunk it if needed
    :param data: A list of input data, initially contains one time which is the data needed to be sent to the model
    :return: A list of the chunked data, if the input doesn't need to be chunked, it will return the same input
    """

    # can't chunk single char
    if len(data[0]) <= 1:
        return data

    # if it contains one value, and it doesn't go beyond the context window then return
    if len(data) == 1 and count_token(data) <= CONTEXT_WINDOW:
        return data

    # the single item has exceeded the context windows
    if len(data) == 1 and count_token(data) > CONTEXT_WINDOW:
        mid = len(data[0]) // 2
        left, right = data[0][:mid], data[0][mid:]
        return chunk_by_context_window([left]) + chunk_by_context_window([right])

    # if items are more one, it checks the context window automatically
    result = []
    for item in data:
        result.extend(chunk_by_context_window([item]))
    return result


def __test_count_tokens():
    with open("../data/scraped_output_example", encoding="utf-8") as f:
        inn = f.read()
        inn = inn * 10
        count = count_token(inn)
        print("count", count)
        print(f"You are using {int(count / CONTEXT_WINDOW * 100)}% of memory")

def __test_chunking():
   with open("../data/scraped_output_example", encoding="utf-8") as f:
        inn = f.read()
        inn = inn * 20
        data = chunk_by_context_window([inn])
        for i, item in enumerate(data):
            print(f"{i+1}. {item.replace("\n", " ")[:100]}")

if __name__ == "__main__":
    # __test_count_tokens()
    __test_chunking()

