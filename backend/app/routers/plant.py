"""
Plant profile router.
"""

import httpx
from fastapi import APIRouter, HTTPException, status, Request
from fastapi.responses import Response
from app.services.qdrant_client import get_qdrant
from app.config import get_settings
from app.utils.text_blob_parser import enrich_payload

router = APIRouter(prefix="/plant", tags=["Plant Profiles"])


@router.api_route("/image-proxy/{plant_id}", methods=["GET", "HEAD"])
async def proxy_plant_image(plant_id: str, request: Request):
    """
    Proxy plant images through the backend to avoid CORS/network issues.

    The frontend should request this endpoint with the plant slug, and we'll
    fetch the image from the original URL and serve it back.

    Supports both GET (with body) and HEAD (headers only) requests.
    """
    try:
        settings = get_settings()
        qdrant = get_qdrant()

        # Get plant data
        points = await qdrant.scroll_points(
            collection=settings.plants_collection,
            filter_conditions={"must": [{"key": "slug", "match": {"value": plant_id}}]},
            limit=1,
        )

        if not points or not points[0]:
            raise HTTPException(status_code=404, detail="Plant not found")

        payload = points[0].get("payload", {})

        # Get image URL - check multiple fields
        image_url = (
            payload.get("image_url")
            or payload.get("reference_images", [{}])[0].get("url")
            or payload.get("reference_images", [{}])[0].get("image_url")
        )

        if not image_url:
            raise HTTPException(status_code=404, detail="No image found for this plant")

        # Fetch and proxy the image
        timeout = httpx.Timeout(10.0, connect=10.0)
        async with httpx.AsyncClient(timeout=timeout, follow_redirects=True) as client:
            resp = await client.get(image_url)
            resp.raise_for_status()

        # Determine content type
        content_type = resp.headers.get("content-type", "image/jpeg")

        # Return headers only for HEAD, full response for GET
        if request.method == "HEAD":
            # Include the same headers a GET would provide where possible.
            # Some clients rely on Content-Length being present for HEAD responses,
            # so mirror the upstream response's content-length when available.
            content_length = resp.headers.get("content-length")
            head_headers = {
                "Cache-Control": "public, max-age=86400",  # Cache for 1 day
            }
            if content_length:
                head_headers["Content-Length"] = content_length
            # FastAPI will set Content-Type using media_type, but include it
            # explicitly in headers for clients that inspect headers only.
            head_headers["Content-Type"] = content_type

            return Response(
                status_code=200,
                media_type=content_type,
                headers=head_headers,
            )
        else:
            return Response(
                content=resp.content,
                media_type=content_type,
                headers={
                    "Cache-Control": "public, max-age=86400",  # Cache for 1 day
                },
            )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to proxy image: {str(e)}",
        )


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
            filter_conditions={"must": [{"key": "slug", "match": {"value": plant_id}}]},
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
            detail=f"Plant '{plant_id}' not found",
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve plant: {str(e)}",
        )
