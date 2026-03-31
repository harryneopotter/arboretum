"""
Text search router.
"""

from fastapi import APIRouter, HTTPException, status
from app.models import SearchRequest, SearchResponseItem
from app.services.qdrant_client import get_qdrant
from app.services.text_embeddings import get_text_embedding, get_sparse_embedding
from app.config import get_settings

router = APIRouter(prefix="/search", tags=["Plant Search"])


@router.post("", response_model=list[SearchResponseItem])
async def search_plants(request: SearchRequest):
    """
    Search plants using hybrid dense + sparse embeddings.

    Steps:
    1. Generate dense 1536-dim embedding
    2. Generate sparse BM25 embedding
    3. Perform hybrid search in plants collection
    4. Return top matches with scores
    """
    try:
        settings = get_settings()
        qdrant = get_qdrant()
        text_service = get_text_embedding()
        sparse_service = get_sparse_embedding()

        # Generate embeddings
        dense_vec = await text_service.embed(request.query)
        sparse_vec = await sparse_service.embed(request.query)

        # Hybrid search
        results = await qdrant.search_dense_sparse(
            collection=settings.plants_collection,
            dense_vector=dense_vec,
            sparse_vector=sparse_vec,
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
