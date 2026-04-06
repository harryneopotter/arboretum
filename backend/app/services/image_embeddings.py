"""
Image embedding service using CLIP.
"""

import os
from typing import Optional
import asyncio
import base64
import io
import torch
from PIL import Image
import httpx


class ImageEmbeddingService:
    """Service for generating CLIP image embeddings."""

    def __init__(self):
        self._model = None
        self._processor = None
        self.dimension = 512
        self.model_name = os.getenv(
            "CLIP_MODEL_NAME",
            "openai/clip-vit-base-patch32",
        )

    @property
    def model(self):
        """Load CLIP model using transformers. Uses pre-bundled model from build if available."""
        if self._model is None:
            import logging
            from pathlib import Path
            import transformers

            logger = logging.getLogger(__name__)

            # Check for pre-bundled model in /root/.cache (from Dockerfile)
            cache_root = Path(os.getenv("HF_HOME", "/root/.cache/huggingface"))
            model_cache = cache_root / "hub"

            logger.info(f"Looking for CLIP model in {model_cache}")

            try:
                from transformers import CLIPModel, CLIPProcessor

                # Try loading from pre-bundled cache first
                self._processor = CLIPProcessor.from_pretrained(self.model_name)
                self._model = CLIPModel.from_pretrained(self.model_name)
                logger.info("CLIP model loaded successfully from cache")
            except Exception as e:
                logger.warning(f"CLIP load from cache failed: {e}", exc_info=True)
                # Fallback: download at runtime (will work if HF_TOKEN is set or rate limit allows)
                logger.info("Falling back to runtime download...")
                self._processor = CLIPProcessor.from_pretrained(self.model_name)
                self._model = CLIPModel.from_pretrained(self.model_name)
        return self._model

    @property
    def processor(self):
        """Return processor (triggers model load via model property)."""
        _ = self.model  # Trigger load if needed
        return self._processor

    async def embed(self, image_data: str | bytes) -> list[float]:
        """Generate CLIP embedding from image."""
        # Trigger lazy load by accessing the property
        _ = self.model
        _ = self.processor

        if isinstance(image_data, str):
            if "," in image_data:
                image_data = image_data.split(",", 1)[1]
            image_bytes = base64.b64decode(image_data)
        else:
            image_bytes = image_data

        image = Image.open(io.BytesIO(image_bytes)).convert("RGB")

        def _encode():
            inputs = self._processor(images=image, return_tensors="pt")
            with torch.no_grad():
                image_features = self._model.get_image_features(**inputs)
            return image_features.squeeze().numpy().tolist()

        embedding = await asyncio.to_thread(_encode)
        return embedding

    async def embed_from_url(self, url: str) -> list[float]:
        """Download image from URL and generate embedding."""
        timeout = httpx.Timeout(connect=5.0, read=30.0, write=30.0, pool=5.0)
        async with httpx.AsyncClient(timeout=timeout) as client:
            resp = await client.get(url)
            resp.raise_for_status()

        image = Image.open(io.BytesIO(resp.content)).convert("RGB")

        def _encode():
            inputs = self._processor(images=image, return_tensors="pt")
            with torch.no_grad():
                image_features = self._model.get_image_features(**inputs)
            return image_features.squeeze().numpy().tolist()

        embedding = await asyncio.to_thread(_encode)
        return embedding


# Singleton instance
_image_service: Optional[ImageEmbeddingService] = None


def get_image_embedding() -> ImageEmbeddingService:
    """Get image embedding service singleton."""
    global _image_service
    if _image_service is None:
        _image_service = ImageEmbeddingService()
    return _image_service
