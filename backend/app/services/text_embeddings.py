"""
Text embedding service using OpenAI text-embedding-3-small.
"""

from typing import Optional
import requests
from app.config import get_settings


class TextEmbeddingService:
    """Service for generating text embeddings."""

    def __init__(self):
        self.settings = get_settings()
        self.api_key = self.settings.openai_api_key
        self.model = self.settings.openai_embedding_model
        self.dimension = self.settings.dense_dim
        self._cache: dict[str, list[float]] = {}

    async def embed(self, text: str, use_cache: bool = True) -> list[float]:
        """
        Generate dense embedding for text.

        Args:
            text: Input text
            use_cache: Whether to cache results

        Returns:
            1536-dim embedding vector
        """
        cache_key = text.lower().strip()
        
        if use_cache and cache_key in self._cache:
            return self._cache[cache_key]

        if not self.api_key:
            # Return deterministic mock for testing
            vector = self._mock_embedding(cache_key)
            if use_cache:
                self._cache[cache_key] = vector
            return vector

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }

        resp = requests.post(
            "https://api.openai.com/v1/embeddings",
            headers=headers,
            json={
                "input": text[:8192],  # Truncate if too long
                "model": self.model,
                "dimensions": self.dimension,
            },
        )
        resp.raise_for_status()

        embedding = resp.json()["data"][0]["embedding"]
        
        if use_cache:
            self._cache[cache_key] = embedding
            
        return embedding

    def _mock_embedding(self, text: str) -> list[float]:
        """Generate deterministic mock embedding from text hash."""
        import hashlib
        # Generate enough bytes for 1536 floats
        h = hashlib.sha256(text.encode()).digest()
        # Repeat to get enough data (1536 floats * 4 bytes = 6144 bytes needed)
        data = (h * (6144 // len(h) + 1))[:6144]
        import struct
        values = struct.unpack("1536f", data)
        # Normalize
        norm = sum(v * v for v in values) ** 0.5
        if norm == 0:
            norm = 1
        return [v / norm for v in values]

    def clear_cache(self):
        """Clear the embedding cache."""
        self._cache.clear()


class SparseEmbeddingService:
    """BM25-style sparse embedding service."""

    def __init__(self):
        self._cache: dict[str, dict[str, float]] = {}

    async def embed(self, text: str, use_cache: bool = True) -> dict[str, float]:
        """
        Generate sparse BM25-style embedding.

        Args:
            text: Input text

        Returns:
            Dict of {token: weight}
        """
        cache_key = text.lower().strip()
        
        if use_cache and cache_key in self._cache:
            return self._cache[cache_key]

        # Tokenize
        tokens = self._tokenize(text)
        
        # Calculate TF-IDF like weights
        weights = self._calculate_weights(tokens)
        
        if use_cache:
            self._cache[cache_key] = weights
            
        return weights

    def _tokenize(self, text: str) -> list[str]:
        """Simple tokenization and normalization."""
        import re
        text = text.lower()
        # Split on non-alphanumeric
        tokens = re.findall(r"[a-z0-9]+", text)
        # Remove stopwords
        stopwords = {
            "a", "an", "the", "and", "or", "but", "in", "on", "at", "to", "for",
            "of", "with", "by", "from", "is", "it", "as", "be", "are", "was",
            "were", "been", "being", "have", "has", "had", "do", "does", "did",
            "will", "would", "could", "should", "may", "might", "can", "this",
            "that", "these", "those", "i", "you", "he", "she", "we", "they",
        }
        return [t for t in tokens if t not in stopwords and len(t) > 1]

    def _calculate_weights(self, tokens: list[str]) -> dict[str, float]:
        """Calculate BM25-like weights."""
        from collections import Counter
        import math

        if not tokens:
            return {}

        tf = Counter(tokens)
        total = len(tokens)

        # IDF-like factor (simplified - assumes corpus of 75 plants)
        idf = {}
        for token in set(tokens):
            # Approximate IDF - tokens appearing in fewer plants get higher weight
            df = sum(1 for t in tf.keys() if t == token)
            idf[token] = math.log((75 + 1) / (df + 1)) + 1

        weights = {}
        for token, count in tf.items():
            tf_norm = count / total
            weights[token] = tf_norm * idf.get(token, 1.0)

        return weights

    def clear_cache(self):
        """Clear the embedding cache."""
        self._cache.clear()


# Singleton instances
_text_service: Optional[TextEmbeddingService] = None
_sparse_service: Optional[SparseEmbeddingService] = None


def get_text_embedding() -> TextEmbeddingService:
    """Get text embedding service singleton."""
    global _text_service
    if _text_service is None:
        _text_service = TextEmbeddingService()
    return _text_service


def get_sparse_embedding() -> SparseEmbeddingService:
    """Get sparse embedding service singleton."""
    global _sparse_service
    if _sparse_service is None:
        _sparse_service = SparseEmbeddingService()
    return _sparse_service
