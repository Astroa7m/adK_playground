import json
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
    with open("../common/current_knowledge_config.json", "r") as f:
        collection_name = json.load(f)['tenant']

    # querying
    result = []
    for query in queries:
        result.extend(query_knowledge_base(query, collection_name))

    # # deduplicating, just making them into a set
    # final = list(set(result))

    return result


if __name__ == "__main__":
    queries = [
        "Awasr opening times",
        "Awasr branch availability",
        "Working hours Awasr",
        "Up time Awasr"

    ]
    print(query_current_knowledge_base(queries))
