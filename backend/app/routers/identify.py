"""
Image identification router.
"""

from fastapi import APIRouter, HTTPException, status
from app.models import IdentifyRequest, IdentifyResponse, IdentifyMatch
from app.services.qdrant_client import get_qdrant
from app.services.image_embeddings import get_image_embedding
from app.config import get_settings
from app.utils.slugify import slugify
from app.utils.text_blob_parser import enrich_payload

router = APIRouter(prefix="/identify", tags=["Image Identification"])

CONFIDENCE_THRESHOLD = 0.3


@router.post("", response_model=IdentifyResponse)
async def identify_plant(request: IdentifyRequest):
    """
    Identify a plant from an image.

    Steps:
    1. Decode base64 image
    2. Generate CLIP embedding (512 dims)
    3. Search plant-images collection
    4. Look up full plant profile by exact slug
    5. Return top 3 matches with plant data; flag uncertain if best score is low
    """
    try:
        settings = get_settings()
        qdrant = get_qdrant()
        image_service = get_image_embedding()

        # Generate CLIP embedding
        image_vector = await image_service.embed(request.image)

        # Search image collection
        image_results = await qdrant.search_image(
            collection=settings.plant_images_collection,
            image_vector=image_vector,
            limit=3,
        )

        if not image_results:
            return IdentifyResponse(matches=[], plant=None, message="No matches found")

        # Build matches — image payloads use plant_slug (set by ingest_plants.py)
        matches = []
        best_slug = None

        for result in image_results:
            payload = result.get("payload", {})
            slug = (
                payload.get("plant_slug")
                or payload.get("slug")
                or slugify(payload.get("plant_name", ""))
            )
            matches.append(IdentifyMatch(
                slug=slug,
                plant_name=payload.get("plant_name", ""),
                score=result.get("score", 0),
                image_url=payload.get("image_url"),
            ))
            if best_slug is None:
                best_slug = slug

        # Low-confidence: return matches but no plant profile, signal uncertainty
        best_score = matches[0].score if matches else 0
        if best_score < CONFIDENCE_THRESHOLD:
            return IdentifyResponse(
                matches=matches,
                plant=None,
                message="Low confidence — try a clearer photo",
            )

        # Fetch full plant profile by exact slug lookup
        plant_data = None
        if best_slug:
            plant_points = await qdrant.scroll_points(
                collection=settings.plants_collection,
                filter_conditions={
                    "must": [{"key": "slug", "match": {"value": best_slug}}]
                },
                limit=1,
            )
            if plant_points:
                plant_data = enrich_payload(plant_points[0].get("payload", {}))

        return IdentifyResponse(matches=matches, plant=plant_data)

    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid image data: {str(e)}"
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Identification failed: {str(e)}"
        )
