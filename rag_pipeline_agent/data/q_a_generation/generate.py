import json

from google import genai
from google.genai import types
from dotenv import load_dotenv
import os
from tqdm import tqdm

from rag_pipeline_agent.data.q_a_generation.token_helper import chunk_by_context_window_if_needed

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

def preprocess_q_a(out_file_path):
    """Converting json list of objects with q/a fields to json list of string concatenating q/a"""""
    with open(out_file_path, encoding="utf-8") as f:
        data = json.load(f)

    dump = [f"Q:{entry["Q"]}A:{entry["A"]}" for entry in data]

    print(dump)
    with open(out_file_path, mode='w', encoding="utf-8") as f:
        json.dump(dump, f, ensure_ascii=False, indent=4)


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

    if not os.path.exists(in_file_path):
        raise FileNotFoundError(f"Input file missing: {in_file_path}. Did you run the cleaner?")

    # getting markdwon data
    with open(in_file_path, encoding="utf-8") as in_f:
        in_data = in_f.read()

    # checking for markdown data size
    try:
        full_content_chunks = chunk_by_context_window_if_needed([in_data])
    except Exception as e:
        raise RuntimeError(f"Chunking failed: {e}")

    for content in full_content_chunks:
        try:
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

            data = json.loads(final_data)

            if not isinstance(data, list):
                raise ValueError("LLM did not return a list of Q/A pairs.")

            dump_json(out_file_path, data)

            print("Done Converting data into Q/A")
        except json.JSONDecodeError as e:
            print(f"Skipping chunk: LLM returned invalid JSON. Error: {e}")
            print(f"Returned response: {data}")
            break
        except Exception as e:
            print(f"Unexpected error during generation: {e}")
            break


if __name__ == "__main__":
    # generate_qa()
    preprocess_q_a(out_file_path)