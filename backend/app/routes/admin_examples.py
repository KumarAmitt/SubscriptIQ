from fastapi import APIRouter, HTTPException, Query
from app.models.schemas import FewShotExampleItem
from app.vector_store.qdrant_store import (
    get_all_examples,
    search_examples,
    add_or_update_example,
    delete_example
)

router = APIRouter(prefix="/admin/examples", tags=["Admin: Examples Manager"])

@router.get("")
async def list_examples(
    search: str | None = Query(None, description="Semantic vector search across examples"),
    query_type: str | None = Query(None, description="Filter by query type")
):
    """
    Returns curated few-shot examples from Qdrant.
    Supports semantic vector search and query type filtering.
    """
    try:
        if search and search.strip():
            results = search_examples(query_text=search.strip(), limit=15, query_type=query_type)
        else:
            all_items = get_all_examples()
            if query_type:
                results = [item for item in all_items if item.get("query_type") == query_type]
            else:
                results = all_items

        return {
            "examples": results,
            "total_count": len(results)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("")
async def create_or_update_example(payload: FewShotExampleItem):
    """
    Adds or updates a few-shot example in Qdrant vector database.
    """
    try:
        data = payload.model_dump()
        saved = add_or_update_example(data)
        return {
            "success": True,
            "example": saved,
            "message": "Few-shot example successfully indexed in Qdrant."
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/{example_id}")
async def remove_example(example_id: int):
    """
    Deletes a few-shot example from Qdrant.
    """
    try:
        success = delete_example(example_id)
        return {
            "success": success,
            "message": f"Example #{example_id} deleted from Qdrant."
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
