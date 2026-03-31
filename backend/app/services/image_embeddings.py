"""
Image embedding service using CLIP.
"""

from typing import Optional
import base64
import io
from PIL import Image
import numpy as np


class ImageEmbeddingService:
    """Service for generating CLIP image embeddings."""

    def __init__(self):
        self._model = None
        self.dimension = 512

    @property
    def model(self):
        """Lazy load CLIP model."""
        if self._model is None:
            from sentence_transformers import SentenceTransformer
            self._model = SentenceTransformer("clip-ViT-B-32")
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

        # Generate embedding
        embedding = self.model.encode([image])[0].tolist()

        return embedding

    def embed_from_url(self, url: str) -> list[float]:
        """
        Download image from URL and generate embedding.

        Args:
            url: Image URL

        Returns:
            512-dim embedding vector
        """
        import requests

        resp = requests.get(url)
        resp.raise_for_status()

        return resp.content


# Singleton instance
_image_service: Optional[ImageEmbeddingService] = None


def get_image_embedding() -> ImageEmbeddingService:
    """Get image embedding service singleton."""
    global _image_service
    if _image_service is None:
        _image_service = ImageEmbeddingService()
    return _image_service
