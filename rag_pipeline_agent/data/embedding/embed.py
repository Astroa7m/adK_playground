import os
import threading
from typing import Optional

from dotenv import load_dotenv
from google import genai
from google.genai import Client, types
from tqdm import tqdm

from rag_pipeline_agent.data.common import BATCH_SIZE, DIMENSION_SIZE

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
        result = embed(batch)
        current_embedded_data = [
            {
                "id": i + j,
                "vector": result.embeddings[j].values,
                "text": batch[j]
            }
            for j in range(len(result.embeddings))
        ]
        embedded_data.extend(current_embedded_data)
    return embedded_data