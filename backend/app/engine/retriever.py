from app.vector_store.qdrant_store import search_examples

def retrieve_examples(query: str, query_type: str | None = None, limit: int = 4) -> list[dict]:
    """
    Step 3: Examples Retriever (Vector Search via Qdrant)
    Retrieves the top-k most similar (question -> SQL) few-shot examples.
    """
    results = search_examples(query_text=query, limit=limit, query_type=query_type)
    # If filtered search was too restrictive, fallback to query search without type constraint
    if len(results) < 2:
        results = search_examples(query_text=query, limit=limit, query_type=None)
    return results

def format_examples_for_prompt(examples: list[dict]) -> str:
    """Formats few-shot examples for inclusion in the SQL Generator prompt."""
    if not examples:
        return ""
    lines = ["### Few-Shot Relevant Examples:"]
    for i, ex in enumerate(examples, 1):
        lines.append(f"Example {i}:")
        lines.append(f"Question: {ex['question']}")
        lines.append(f"SQL: {ex['sql']}")
        if ex.get("explanation"):
            lines.append(f"Explanation: {ex['explanation']}")
        lines.append("")
    return "\n".join(lines)
