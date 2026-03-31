"""
Plant profile router.
"""

from fastapi import APIRouter, HTTPException, status
from app.services.qdrant_client import get_qdrant
from app.config import get_settings
from app.utils.text_blob_parser import enrich_payload

router = APIRouter(prefix="/plant", tags=["Plant Profiles"])


@router.get("/{plant_id}")
async def get_plant_profile(plant_id: str):
    """
    Retrieve full plant profile by ID (slug).

    Args:
        plant_id: Plant slug (e.g., 'chinese-evergreen-aglaonema')

    Returns:
        Full plant JSON payload with structured care/description/problems
    """
    try:
        settings = get_settings()
        qdrant = get_qdrant()

        # Search by slug using Qdrant filter (avoids full-collection scan)
        points = await qdrant.scroll_points(
            collection=settings.plants_collection,
            filter_conditions={
                "must": [{"key": "slug", "match": {"value": plant_id}}]
            },
            limit=1,
        )

        if points:
            payload = enrich_payload(points[0].get("payload", {}))
            return payload

        # Fallback: also try matching plant_id field for legacy data
        points = await qdrant.scroll_points(
            collection=settings.plants_collection,
            filter_conditions={
                "must": [{"key": "plant_id", "match": {"value": plant_id}}]
            },
            limit=1,
        )

        if points:
            payload = enrich_payload(points[0].get("payload", {}))
            return payload

        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Plant '{plant_id}' not found"
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve plant: {str(e)}"
        )
