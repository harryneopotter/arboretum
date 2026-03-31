"""
Plant profile router.
"""

from fastapi import APIRouter, HTTPException, status
from app.services.qdrant_client import get_qdrant
from app.config import get_settings

router = APIRouter(prefix="/plant", tags=["Plant Profiles"])


@router.get("/{plant_id}")
async def get_plant_profile(plant_id: str):
    """
    Retrieve full plant profile by ID (slug).

    Args:
        plant_id: Plant slug (e.g., 'chinese-evergreen-aglaonema')

    Returns:
        Full plant JSON payload
    """
    try:
        settings = get_settings()
        qdrant = get_qdrant()

        # Scroll through all plants (75 total, small dataset)
        # Filter in-memory since slug field may not be indexed
        offset = None
        while True:
            body = {
                "limit": 100,
                "with_payload": True,
                "with_vectors": False,
            }
            if offset:
                body["offset"] = offset

            import requests
            resp = requests.post(
                f"{settings.qdrant_url}/collections/{settings.plants_collection}/points/scroll",
                headers={"api-key": settings.qdrant_api_key, "Content-Type": "application/json"},
                json=body,
            )
            resp.raise_for_status()
            data = resp.json().get("result", {})
            points = data.get("points", [])

            for point in points:
                payload = point.get("payload", {})
                # Match by slug or plant_id
                if payload.get("slug") == plant_id or payload.get("plant_id") == plant_id:
                    return payload

            # Check if more pages
            next_page = data.get("next_page_offset")
            if not next_page:
                break
            offset = next_page

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
