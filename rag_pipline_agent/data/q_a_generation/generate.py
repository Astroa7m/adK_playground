import json

from google import genai
from google.genai import types
from dotenv import load_dotenv
import os
from tqdm import tqdm

from rag_pipline_agent.data.q_a_generation.token_helper import chunk_by_context_window_if_needed

load_dotenv()

api_key = os.getenv("GOOGLE_API_KEY")
client = genai.Client(api_key=api_key)

system_prompt = """
You will be provided with website-scraped data in Markdown format.  
Your task is to transform this data into a comprehensive Question/Answer dataset in English, suitable for model training.  

Guidelines:
- Cover all information contained in the provided data.  
- Each entry must be expressed as a Q/A pair.  
- Output must be in **pure JSON format** only.  
- Do not include greetings, explanations, or conclusions.  

Example output format:
[
    {
        "Q": "What is [example question]?",
        "A": "[example answer]"
    },
    {
        "Q": "How does [example process] work?",
        "A": "[example answer]"
    }
]
"""

in_file_path = "../common/scraped_output_example_cleaned.md"
out_file_path = "../common/q_a.json"



def dump_json(out_file_path: str, extra_data: list):

    if os.path.exists(out_file_path):
        with open(out_file_path, "r", encoding="utf-8") as f:
            data = json.load(f)

        data.extend(extra_data)

        with open(out_file_path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=4)

    else:
        with open(out_file_path, "w", encoding="utf-8") as f:
            json.dump(extra_data, f, ensure_ascii=False, indent=4)

def generate_qa():
    # getting markdwon data
    with open(in_file_path, encoding="utf-8") as in_f:
        in_data = in_f.read()

    # checking for markdown data size

    full_content_chunks = chunk_by_context_window_if_needed([in_data])

    for content in full_content_chunks:

        response = client.models.generate_content_stream(
            model="gemini-2.5-flash-lite",
            contents=content,
            config=types.GenerateContentConfig(
                system_instruction=system_prompt
            )
        )

        final_data = ""

        for chunk in tqdm(response, desc="Streaming chunks", unit="chunk"):
            final_data += chunk.text

        # removing backticks and 'json'
        final_data = final_data.replace("`", "").replace("json", "")

        print("/"*50, "BEGIN FOR DEBUGGING", "/"*50)
        print(final_data)
        print("/"*50, "END FOR DEBUGGING", "/"*50)

        # check if final data is actually parserable to json
        try:
            data = json.loads(final_data)
        except Exception as e:
            print("Error converting model response to json", e)
            # we should like retry but will leave it for later
            return

        dump_json(out_file_path, data)

        print("Done Converting data into Q/A")



if __name__ == "__main__":
    generate_qa()