import os
import threading
import time
from typing import Optional

from dotenv import load_dotenv
from google import genai
from google.genai import Client, types
from tqdm import tqdm

BATCH_SIZE = 100
DIMENSION_SIZE = 768
load_dotenv()
api_key = os.getenv("GOOGLE_API_KEY")
gemini_client: Optional[Client] = None

_lock = threading.Lock()


def ensure_gemini_client():
    global gemini_client
    if gemini_client is None:
        with _lock:
            if gemini_client is None:
                gemini_client = genai.Client(api_key=api_key)


def generate_id():
    time.sleep(0.001)
    return int(time.time() * 1000)


def embed(contents, model="gemini-embedding-001"):
    ensure_gemini_client()
    return gemini_client.models.embed_content(
        model=model,
        contents=contents,
        config=types.EmbedContentConfig(output_dimensionality=DIMENSION_SIZE)
    )


def embed_and_get_result(data):
    """embeds data and returns object containing info about the data
    e.g.:
    {
        "id": ...,
        "vector": ....,
        "text":...,
    }
    """
    ensure_gemini_client()
    embedded_data = []
    for i in tqdm(range(0, len(data), BATCH_SIZE), desc="Embedding batches"):
        batch = data[i:i + BATCH_SIZE]
        result = embed(str(batch))
        current_embedded_data = [
            {
                "id": generate_id(),
                "vector": result.embeddings[j].values,
                "text": batch[j]
            }
            for j in range(len(result.embeddings))
        ]
        embedded_data.extend(current_embedded_data)
    return embedded_data
