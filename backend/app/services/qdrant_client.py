"""
Qdrant client service for vector database operations.
"""

import httpx
from typing import Optional
from app.config import get_settings


class QdrantService:
    """Service for Qdrant vector database operations."""

    def __init__(self):
        self.settings = get_settings()
        self.url = self.settings.qdrant_url
        self.key = self.settings.qdrant_api_key
        self.headers = {"api-key": self.key, "Content-Type": "application/json"}
        self.timeout = httpx.Timeout(connect=5.0, read=30.0, write=30.0, pool=5.0)

    async def _request_json(self, method: str, path: str, json: dict | None = None) -> dict:
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            response = await client.request(
                method=method,
                url=f"{self.url}{path}",
                headers=self.headers,
                json=json,
            )
            response.raise_for_status()
            return response.json()

    # -------------------------------------------------------------------------
    # Search Methods
    # -------------------------------------------------------------------------

    async def search_dense_sparse(
        self,
        collection: str,
        dense_vector: list[float],
        sparse_vector: dict[str, float] | None = None,
        limit: int = 5,
        filter_conditions: dict | None = None,
    ) -> list[dict]:
        """
        Search using dense vectors.

        Args:
            collection: Collection name
            dense_vector: Dense embedding vector
            sparse_vector: Reserved for future use
            limit: Max results
            filter_conditions: Optional Qdrant filter

        Returns:
            List of match dicts with id, score, payload
        """
        body = {
            "vector": {
                "name": self.settings.dense_vector_name,
                "vector": dense_vector
            },
            "limit": limit,
            "with_payload": True,
            "with_vector": False,
        }

        if filter_conditions:
            body["filter"] = filter_conditions

        response = await self._request_json(
            "POST",
            f"/collections/{collection}/points/search",
            json=body,
        )
        return response.get("result", [])

    async def search_image(
        self,
        collection: str,
        image_vector: list[float],
        limit: int = 5,
    ) -> list[dict]:
        """
        Search image collection by vector.

        Args:
            collection: Collection name (plant-images)
            image_vector: CLIP embedding vector
            limit: Max results

        Returns:
            List of match dicts with id, score, payload
        """
        body = {
            "vector": {
                "name": self.settings.image_vector_name,
                "vector": image_vector
            },
            "limit": limit,
            "with_payload": True,
            "with_vector": False,
        }

        response = await self._request_json(
            "POST",
            f"/collections/{collection}/points/search",
            json=body,
        )
        return response.get("result", [])

    async def get_point(
        self,
        collection: str,
        point_id: int | str,
    ) -> dict | None:
        """
        Get a single point by ID.

        Args:
            collection: Collection name
            point_id: Point ID

        Returns:
            Point dict or None
        """
        try:
            response = await self._request_json(
                "GET",
                f"/collections/{collection}/points/{point_id}",
            )
        except httpx.HTTPStatusError as exc:
            if exc.response.status_code == 404:
                return None
            raise

        if not response:
            return None

        return response.get("result")

    async def scroll_points(
        self,
        collection: str,
        filter_conditions: dict | None = None,
        limit: int = 100,
    ) -> list[dict]:
        """
        Scroll through points with optional filter.

        Args:
            collection: Collection name
            filter_conditions: Optional Qdrant filter
            limit: Page size

        Returns:
            List of point dicts
        """
        body = {
            "limit": limit,
            "with_payload": True,
            "with_vector": False,
        }

        if filter_conditions:
            body["filter"] = filter_conditions

        response = await self._request_json(
            "POST",
            f"/collections/{collection}/points/scroll",
            json=body,
        )
        return response.get("result", {}).get("points", [])

    async def retrieve(
        self,
        collection: str,
        ids: list[int | str],
    ) -> list[dict]:
        """
        Retrieve points by IDs.

        Args:
            collection: Collection name
            ids: List of point IDs

        Returns:
            List of point dicts with payload
        """
        body = {"ids": ids}

        response = await self._request_json(
            "POST",
            f"/collections/{collection}/points/retrieve",
            json=body,
        )
        return response.get("result", [])


# Singleton instance
_qdrant_service: Optional[QdrantService] = None


def get_qdrant() -> QdrantService:
    """Get Qdrant service singleton."""
    global _qdrant_service
    if _qdrant_service is None:
        _qdrant_service = QdrantService()
    return _qdrant_service
