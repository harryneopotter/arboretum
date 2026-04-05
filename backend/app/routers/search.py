"""
Text search router.
"""

from fastapi import APIRouter, HTTPException, status
from app.models import SearchRequest, SearchResponseItem
from app.services.qdrant_client import get_qdrant
from app.services.text_embeddings import get_text_embedding
from app.config import get_settings

router = APIRouter(prefix="/search", tags=["Plant Search"])


@router.post("", response_model=list[SearchResponseItem])
async def search_plants(request: SearchRequest):
    """
    Search plants using dense semantic embeddings.

    Steps:
    1. Generate dense 1536-dim embedding
    2. Search plants collection by dense vector similarity
    3. Return top matches with scores
    """
    try:
        settings = get_settings()
        qdrant = get_qdrant()
        text_service = get_text_embedding()

        # Generate dense embedding
        dense_vec = await text_service.embed(request.query)

        # Dense semantic search
        results = await qdrant.search_dense_sparse(
            collection=settings.plants_collection,
            dense_vector=dense_vec,
            limit=request.limit,
        )

        if not results:
            return []

        # Build response
        items = []
        for result in results:
            payload = result.get("payload", {})
            slug = payload.get("slug") or payload.get("plant_id") or ""
            items.append(SearchResponseItem(
                slug=slug,
                plant_name=payload.get("plant_name", ""),
                score=result.get("score", 0),
                category=payload.get("category"),
                description=payload.get("description"),
            ))

        return items

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Search failed: {str(e)}"
        )
