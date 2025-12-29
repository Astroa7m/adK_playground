import json
from pathlib import Path
from typing import List

from rag_pipeline_agent.db.db_pipeline import query_knowledge_base


def query_current_knowledge_base(queries: List[str]) -> List[str]:
    """
    Retrieves relevant documents from the active knowledge base using semantic search.

    When to use this tool:
    - User asks questions that require information from the knowledge base
    - User requests specific facts, data, or information you don't have in your training
    - Any query about the content within the selected knowledge base

    Query generation strategy:
    Generate 3-5 diverse query variants to maximize retrieval quality:
    - Rephrase the user's question in different ways
    - Break complex questions into simpler sub-queries
    - Use synonyms and alternative terminology
    - Vary between question and keyword formats

    Example:
    User asks: "What were the opening times for Omantel?"
    Generate queries like:
    1. "Omantel opening times"
    2. "Omantel branch availability"
    3. "Working hours Omantel"
    4. "Up time Omantel"

    Args:
        queries (List[str]): 3-5 diverse query variants (minimum 3, maximum 5)

    Returns:
        List[str]: Deduplicated list of retrieved documents relevant to the queries
    """
    # getting the knowledge base
    config_path = Path(__file__).parent.parent / "common/current_knowledge_config.json"
    with open(config_path, "r") as f:
        tenant_name = json.load(f)['tenant']

    # querying
    result = []
    for query in queries:
        result.extend(query_knowledge_base(query, tenant_name))


    deduplicated = []
    seen = set()
    # deduplicate
    for r in result:
        if r['text'] not in seen:
            # only need text and distance
            needed_row = {
                "text": r["text"],
                "distance": r["distance"]
            }
            deduplicated.append(needed_row)
            seen.add(r['text'])



    # sort by distance desc (default is cosine, the more the better)
    sorted_result = sorted(deduplicated, key=lambda x: x['distance'], reverse=True)


    # final result the llm will only see the text
    final_result = [r["text"] for r in sorted_result]

    return final_result


if __name__ == "__main__":
    queries = [
        "Awasr opening times",
        "Awasr branch availability",
        "Working hours Awasr",
        "Up time Awasr"

    ]
    print(query_current_knowledge_base(queries))
