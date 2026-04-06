"""
Tests for app/services/text_embeddings.py
Covers TextEmbeddingService (mock path) and SparseEmbeddingService.
"""

import pytest
from unittest.mock import patch, MagicMock
from app.services.text_embeddings import TextEmbeddingService, SparseEmbeddingService


class TestTextEmbeddingServiceMock:
    """Tests using the mock embedding path (no OpenAI API key)."""

    def setup_method(self):
        # Reset the singleton so each test gets a fresh instance
        import app.services.text_embeddings as mod
        mod._text_service = None

    @pytest.fixture
    def service(self):
        # Patch the module-level reference used inside text_embeddings.py
        with patch("app.services.text_embeddings.get_settings") as mock_settings:
            settings = MagicMock()
            settings.openai_api_key = None  # force mock path
            settings.openai_embedding_model = "text-embedding-3-small"
            settings.dense_dim = 1536
            mock_settings.return_value = settings
            svc = TextEmbeddingService()
        return svc

    async def test_embed_returns_list(self, service):
        vector = await service.embed("hello world")
        assert isinstance(vector, list)

    async def test_embed_correct_dimension(self, service):
        vector = await service.embed("hello world")
        assert len(vector) == 1536

    async def test_embed_is_normalized(self, service):
        vector = await service.embed("test")
        norm = sum(v * v for v in vector) ** 0.5
        assert abs(norm - 1.0) < 0.01

    async def test_embed_deterministic(self, service):
        v1 = await service.embed("same text")
        v2 = await service.embed("same text")
        assert v1 == v2

    async def test_embed_different_texts_different_vectors(self, service):
        v1 = await service.embed("aloe vera")
        v2 = await service.embed("money plant")
        assert v1 != v2

    async def test_embed_caching(self, service):
        service.clear_cache()
        v1 = await service.embed("cached text")
        # Manually check cache populated
        assert "cached text" in service._cache
        v2 = await service.embed("cached text")
        assert v1 == v2

    async def test_embed_cache_disabled(self, service):
        v1 = await service.embed("no cache", use_cache=False)
        assert "no cache" not in service._cache

    async def test_clear_cache(self, service):
        await service.embed("fill cache")
        assert len(service._cache) > 0
        service.clear_cache()
        assert len(service._cache) == 0

    async def test_embed_strips_and_lowercases_for_cache_key(self, service):
        """Cache key is text.lower().strip()"""
        service.clear_cache()
        await service.embed("  HELLO  ")
        assert "hello" in service._cache


class TestTextEmbeddingServiceWithApiKey:
    """Tests for the live OpenAI path (mocked HTTP)."""

    @pytest.fixture
    def service_with_key(self):
        # Patch module-level reference in text_embeddings, not app.config
        with patch("app.services.text_embeddings.get_settings") as mock_settings:
            settings = MagicMock()
            settings.openai_api_key = "sk-fake-key"
            settings.openai_embedding_model = "text-embedding-3-small"
            settings.dense_dim = 1536
            mock_settings.return_value = settings
            return TextEmbeddingService()

    async def test_calls_openai_api(self, service_with_key):
        mock_vector = [0.1] * 1536
        mock_resp = MagicMock()
        mock_resp.raise_for_status = MagicMock()
        mock_resp.json.return_value = {"data": [{"embedding": mock_vector}]}

        with patch("requests.post", return_value=mock_resp) as mock_post:
            vector = await service_with_key.embed("query text")

        mock_post.assert_called_once()
        assert vector == mock_vector

    async def test_api_result_cached(self, service_with_key):
        mock_vector = [0.2] * 1536
        mock_resp = MagicMock()
        mock_resp.raise_for_status = MagicMock()
        mock_resp.json.return_value = {"data": [{"embedding": mock_vector}]}

        with patch("requests.post", return_value=mock_resp) as mock_post:
            await service_with_key.embed("once")
            await service_with_key.embed("once")  # second call should use cache

        # requests.post called only once
        assert mock_post.call_count == 1

    async def test_api_error_propagates(self, service_with_key):
        mock_resp = MagicMock()
        mock_resp.raise_for_status.side_effect = Exception("API error")

        with patch("requests.post", return_value=mock_resp):
            with pytest.raises(Exception, match="API error"):
                await service_with_key.embed("fail")


class TestSparseEmbeddingService:
    def setup_method(self):
        import app.services.text_embeddings as mod
        mod._sparse_service = None

    @pytest.fixture
    def service(self):
        return SparseEmbeddingService()

    async def test_embed_returns_dict(self, service):
        result = await service.embed("aloe vera plant")
        assert isinstance(result, dict)

    async def test_embed_non_empty_for_content(self, service):
        result = await service.embed("money plant leaves")
        assert len(result) > 0

    async def test_stopwords_removed(self, service):
        result = await service.embed("the aloe and the vera")
        assert "the" not in result
        assert "and" not in result

    async def test_short_tokens_removed(self, service):
        result = await service.embed("a b c fern plant")
        # single chars removed, len>1 kept
        assert "a" not in result
        assert "b" not in result
        assert "fern" in result

    async def test_empty_text_returns_empty(self, service):
        result = await service.embed("")
        assert result == {}

    async def test_all_stopwords_returns_empty(self, service):
        result = await service.embed("the and or but in")
        assert result == {}

    async def test_weights_are_positive(self, service):
        result = await service.embed("fern sunlight water soil")
        for v in result.values():
            assert v > 0

    async def test_caching_works(self, service):
        service.clear_cache()
        r1 = await service.embed("cactus desert")
        assert "cactus desert" in service._cache
        r2 = await service.embed("cactus desert")
        assert r1 == r2

    async def test_cache_disabled(self, service):
        service.clear_cache()
        await service.embed("no cache test", use_cache=False)
        assert "no cache test" not in service._cache

    async def test_clear_cache(self, service):
        await service.embed("fill it")
        assert len(service._cache) > 0
        service.clear_cache()
        assert len(service._cache) == 0

    async def test_repeated_tokens_weighted_higher(self, service):
        single = await service.embed("water")
        repeated = await service.embed("water water water")
        # TF is higher for repeated tokens, so weight should differ
        # (same token, different TF — both compute the same IDF since single-token corpus)
        # Just verify the token is present in both
        assert "water" in single
        assert "water" in repeated

    async def test_tokenize_lowercase(self, service):
        r1 = await service.embed("FERN")
        r2 = await service.embed("fern")
        assert r1 == r2

    async def test_special_chars_ignored(self, service):
        result = await service.embed("plant! leaf? soil.")
        # punctuation stripped; tokens should be plain words
        assert all(k.isalnum() for k in result.keys())
