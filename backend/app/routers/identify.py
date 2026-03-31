"""
Image identification router.
"""

from fastapi import APIRouter, HTTPException, status
from app.models import IdentifyRequest, IdentifyResponse, IdentifyMatch
from app.services.qdrant_client import get_qdrant
from app.services.image_embeddings import get_image_embedding
from app.config import get_settings
from app.utils.slugify import slugify

router = APIRouter(prefix="/identify", tags=["Image Identification"])


@router.post("", response_model=IdentifyResponse)
async def identify_plant(request: IdentifyRequest):
    """
    Identify a plant from an image.

    Steps:
    1. Decode base64 image
    2. Generate CLIP embedding (512 dims)
    3. Search plant-images collection
    4. Return top 3 matches with full plant data
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
            return IdentifyResponse(matches=[], plant=None)

        # Build matches
        matches = []
        best_plant_id = None

        for result in image_results:
            payload = result.get("payload", {})
            slug = payload.get("slug") or payload.get("plant_id") or slugify(payload.get("plant_name", ""))
            matches.append(IdentifyMatch(
                slug=slug,
                plant_id=payload.get("plant_id", ""),
                plant_name=payload.get("plant_name", ""),
                score=result.get("score", 0),
                image_url=payload.get("image_url"),
            ))
            if best_plant_id is None:
                best_plant_id = payload.get("plant_id") or slug or payload.get("plant_name")

        # Fetch full plant profile
        plant_data = None
        if best_plant_id:
            # Search plants collection for the identified plant
            from app.services.text_embeddings import get_text_embedding
            text_service = get_text_embedding()

            # Embed plant name to do a quick search
            plant_vector = await text_service.embed(best_plant_id.replace("_", " "))
            
            plant_results = await qdrant.search_dense_sparse(
                collection=settings.plants_collection,
                dense_vector=plant_vector,
                limit=1,
            )

            if plant_results:
                plant_data = plant_results[0].get("payload")

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
