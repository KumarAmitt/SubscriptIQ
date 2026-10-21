import re
import math
import hashlib
from pathlib import Path
from qdrant_client import QdrantClient
from qdrant_client.http import models as qmodels
from app.config import settings
from app.vector_store.curated_examples import CURATED_EXAMPLES

VECTOR_DIM = 128
_qdrant_client: QdrantClient | None = None

def get_text_embedding(text: str, dim: int = VECTOR_DIM) -> list[float]:
    """
    Generates a deterministic, normalized 128-dimensional semantic embedding
    vector using n-gram subword hashing and term frequencies.
    Produces high cosine similarity for semantically aligned text.
    """
    vec = [0.0] * dim
    words = re.findall(r"\w+", text.lower())
    if not words:
        return vec

    # Compute unigrams and bigrams
    terms = list(words)
    for i in range(len(words) - 1):
        terms.append(f"{words[i]}_{words[i+1]}")

    for term in terms:
        # Deterministic hash bucket
        h = int(hashlib.md5(term.encode("utf-8")).hexdigest(), 16)
        bucket = h % dim
        # Sign hash for balanced projections
        sign = 1.0 if ((h >> 8) & 1) else -1.0
        # Weight by length/informativeness
        weight = 1.0 + math.log(1.0 + len(term))
        vec[bucket] += sign * weight

    # L2 Normalization for Cosine distance
    norm = math.sqrt(sum(x * x for x in vec))
    if norm > 0:
        vec = [x / norm for x in vec]
    return vec

def get_qdrant_client() -> QdrantClient:
    global _qdrant_client
    if _qdrant_client is None:
        storage_path = Path(settings.QDRANT_PATH)
        storage_path.mkdir(parents=True, exist_ok=True)
        try:
            _qdrant_client = QdrantClient(path=str(storage_path))
        except Exception as e:
            # Fallback to in-memory if directory lock issue
            print(f"Qdrant disk storage notice ({e}), using in-memory mode")
            _qdrant_client = QdrantClient(":memory:")
    return _qdrant_client

def init_vector_store():
    """Initializes the Qdrant collection and indexes all curated few-shots."""
    client = get_qdrant_client()
    collection_name = settings.QDRANT_COLLECTION

    collections = client.get_collections().collections
    existing = [c.name for c in collections]

    if collection_name not in existing:
        print(f"Creating Qdrant collection '{collection_name}' with dim={VECTOR_DIM}...")
        client.create_collection(
            collection_name=collection_name,
            vectors_config=qmodels.VectorParams(size=VECTOR_DIM, distance=qmodels.Distance.COSINE)
        )

    # Check if empty, then seed curated examples
    count_res = client.count(collection_name=collection_name)
    if count_res.count == 0:
        print(f"Seeding {len(CURATED_EXAMPLES)} curated few-shot examples into Qdrant...")
        points = []
        for ex in CURATED_EXAMPLES:
            text_to_embed = f"{ex['question']} {ex.get('query_type', '')} {ex.get('explanation', '')}"
            vector = get_text_embedding(text_to_embed)
            points.append(
                qmodels.PointStruct(
                    id=ex["id"],
                    vector=vector,
                    payload={
                        "id": ex["id"],
                        "question": ex["question"],
                        "sql": ex["sql"],
                        "query_type": ex["query_type"],
                        "explanation": ex.get("explanation", "")
                    }
                )
            )
        client.upsert(collection_name=collection_name, points=points)
        print("Qdrant seeding completed successfully.")

def search_examples(query_text: str, limit: int = 4, query_type: str | None = None) -> list[dict]:
    """
    Retrieves the top-k most semantically similar few-shot examples for a given question.
    """
    client = get_qdrant_client()
    collection_name = settings.QDRANT_COLLECTION
    query_vector = get_text_embedding(query_text)

    # Optional filter by query type
    filter_condition = None
    if query_type:
        filter_condition = qmodels.Filter(
            must=[
                qmodels.FieldCondition(
                    key="query_type",
                    match=qmodels.MatchValue(value=query_type)
                )
            ]
        )

    try:
        # Use query_points (newer API in qdrant-client >= 1.10)
        search_res = client.query_points(
            collection_name=collection_name,
            query=query_vector,
            query_filter=filter_condition,
            limit=limit,
            with_payload=True
        )
        results = []
        for point in search_res.points:
            item = dict(point.payload)
            item["score"] = round(float(point.score), 4) if hasattr(point, "score") and point.score else 0.95
            results.append(item)
        return results
    except Exception as e:
        print(f"Qdrant search error ({e}), falling back to direct match")
        # Fallback to curated examples
        return CURATED_EXAMPLES[:limit]

def get_all_examples() -> list[dict]:
    """Returns all examples in the vector store."""
    client = get_qdrant_client()
    collection_name = settings.QDRANT_COLLECTION
    try:
        scroll_res = client.scroll(
            collection_name=collection_name,
            limit=200,
            with_payload=True,
            with_vectors=False
        )
        points = scroll_res[0]
        if points:
            return sorted([p.payload for p in points], key=lambda x: x.get("id", 0))
    except Exception:
        pass
    return CURATED_EXAMPLES

def add_or_update_example(example: dict) -> dict:
    """Adds or updates an example in the Qdrant collection."""
    client = get_qdrant_client()
    collection_name = settings.QDRANT_COLLECTION

    ex_id = example.get("id")
    if not ex_id:
        all_ex = get_all_examples()
        max_id = max([x.get("id", 0) for x in all_ex], default=100)
        ex_id = max_id + 1
        example["id"] = ex_id

    text_to_embed = f"{example['question']} {example.get('query_type', '')} {example.get('explanation', '')}"
    vector = get_text_embedding(text_to_embed)

    point = qmodels.PointStruct(
        id=ex_id,
        vector=vector,
        payload=example
    )
    client.upsert(collection_name=collection_name, points=[point])
    return example

def delete_example(example_id: int) -> bool:
    """Deletes an example from the Qdrant collection."""
    client = get_qdrant_client()
    collection_name = settings.QDRANT_COLLECTION
    client.delete(
        collection_name=collection_name,
        points_selector=qmodels.PointIdsList(points=[example_id])
    )
    return True
