"""
Image embedding service using CLIP.
"""

import os
from typing import Optional
import asyncio
import base64
import io
from PIL import Image
import httpx


class ImageEmbeddingService:
    """Service for generating CLIP image embeddings."""

    def __init__(self):
        self._model = None
        self.dimension = 512
        self.model_name = os.getenv(
            "CLIP_MODEL_NAME",
            "sentence-transformers/clip-ViT-B-32",
        )

    @property
    def model(self):
        """Lazy load CLIP model."""
        if self._model is None:
            from sentence_transformers import SentenceTransformer
            self._model = SentenceTransformer(self.model_name)
        return self._model

    async def embed(self, image_data: str | bytes) -> list[float]:
        """
        Generate CLIP embedding from image.

        Args:
            image_data: Base64 string or bytes of image

        Returns:
            512-dim embedding vector
        """
        # Decode image
        if isinstance(image_data, str):
            # Remove data URL prefix if present
            if "," in image_data:
                image_data = image_data.split(",", 1)[1]
            image_bytes = base64.b64decode(image_data)
        else:
            image_bytes = image_data

        # Load and preprocess image
        image = Image.open(io.BytesIO(image_bytes)).convert("RGB")

        # Run heavy model inference off the event loop.
        embedding = await asyncio.to_thread(
            lambda: self.model.encode(image, normalize_embeddings=True).tolist()
        )

        return embedding

    async def embed_from_url(self, url: str) -> list[float]:
        """
        Download image from URL and generate embedding.

        Args:
            url: Image URL

        Returns:
            512-dim embedding vector
        """
        timeout = httpx.Timeout(connect=5.0, read=30.0, write=30.0, pool=5.0)
        async with httpx.AsyncClient(timeout=timeout) as client:
            resp = await client.get(url)
            resp.raise_for_status()

        image = Image.open(io.BytesIO(resp.content)).convert("RGB")
        embedding = await asyncio.to_thread(
            lambda: self.model.encode(image, normalize_embeddings=True).tolist()
        )
        return embedding


# Singleton instance
_image_service: Optional[ImageEmbeddingService] = None


def get_image_embedding() -> ImageEmbeddingService:
    """Get image embedding service singleton."""
    global _image_service
    if _image_service is None:
        _image_service = ImageEmbeddingService()
    return _image_service
