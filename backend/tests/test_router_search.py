"""
Tests for POST /search endpoint.
Text embedding and Qdrant services are mocked.
"""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from fastapi.testclient import TestClient


MOCK_SEARCH_RESULTS = [
    {
        "score": 0.91,
        "payload": {
            "slug": "money-plant",
            "plant_name": "Money Plant",
            "category": "Indoor",
            "description": "A popular trailing vine.",
        },
    },
    {
        "score": 0.75,
        "payload": {
            "slug": "aloe-vera",
            "plant_name": "Aloe Vera",
            "category": "Succulent",
            "description": "A succulent with medicinal properties.",
        },
    },
]


@pytest.fixture
def mock_services():
    mock_qdrant = MagicMock()
    mock_qdrant.search_dense_sparse = AsyncMock(return_value=MOCK_SEARCH_RESULTS)

    mock_text_svc = MagicMock()
    mock_text_svc.embed = AsyncMock(return_value=[0.1] * 1536)

    mock_sparse_svc = MagicMock()
    mock_sparse_svc.embed = AsyncMock(return_value={"plant": 0.8, "indoor": 0.5})

    return mock_qdrant, mock_text_svc, mock_sparse_svc


@pytest.fixture
def search_client(mock_services, use_temp_db):
    mock_qdrant, mock_text_svc, mock_sparse_svc = mock_services
    with (
        patch("app.routers.search.get_qdrant", return_value=mock_qdrant),
        patch("app.routers.search.get_text_embedding", return_value=mock_text_svc),
        patch("app.routers.search.get_sparse_embedding", return_value=mock_sparse_svc),
    ):
        from app.main import app
        with TestClient(app) as c:
            yield c, mock_qdrant, mock_text_svc, mock_sparse_svc


class TestSearchEndpoint:
    def test_search_returns_results(self, search_client):
        client, *_ = search_client
        resp = client.post("/search", json={"query": "indoor plant"})
        assert resp.status_code == 200
        data = resp.json()
        assert len(data) == 2

    def test_search_result_shape(self, search_client):
        client, *_ = search_client
        resp = client.post("/search", json={"query": "plant"})
        item = resp.json()[0]
        assert "slug" in item
        assert "plant_name" in item
        assert "score" in item

    def test_search_returns_slugs(self, search_client):
        client, *_ = search_client
        resp = client.post("/search", json={"query": "plant"})
        slugs = [i["slug"] for i in resp.json()]
        assert "money-plant" in slugs

    def test_search_with_custom_limit(self, search_client):
        client, _, text_svc, sparse_svc = search_client
        resp = client.post("/search", json={"query": "fern", "limit": 3})
        assert resp.status_code == 200

    def test_search_empty_results(self, search_client):
        client, qdrant, *_ = search_client
        qdrant.search_dense_sparse.return_value = []
        resp = client.post("/search", json={"query": "unknown plant"})
        assert resp.status_code == 200
        assert resp.json() == []

    def test_search_calls_text_embedding(self, search_client):
        client, _, text_svc, _ = search_client
        client.post("/search", json={"query": "aloe vera"})
        text_svc.embed.assert_called_once_with("aloe vera")

    def test_search_calls_sparse_embedding(self, search_client):
        client, _, _, sparse_svc = search_client
        client.post("/search", json={"query": "cactus"})
        sparse_svc.embed.assert_called_once_with("cactus")

    def test_search_empty_query_rejected(self, search_client):
        client, *_ = search_client
        resp = client.post("/search", json={"query": ""})
        assert resp.status_code == 422  # Pydantic validation error

    def test_search_missing_query_rejected(self, search_client):
        client, *_ = search_client
        resp = client.post("/search", json={})
        assert resp.status_code == 422

    def test_search_limit_too_high_rejected(self, search_client):
        client, *_ = search_client
        resp = client.post("/search", json={"query": "plant", "limit": 100})
        assert resp.status_code == 422

    def test_search_qdrant_error_returns_500(self, search_client):
        client, qdrant, *_ = search_client
        qdrant.search_dense_sparse.side_effect = Exception("Qdrant down")
        resp = client.post("/search", json={"query": "plant"})
        assert resp.status_code == 500
        assert "Search failed" in resp.json()["detail"]

    def test_search_category_in_response(self, search_client):
        client, *_ = search_client
        resp = client.post("/search", json={"query": "indoor"})
        item = resp.json()[0]
        assert item["category"] == "Indoor"

    def test_search_description_in_response(self, search_client):
        client, *_ = search_client
        resp = client.post("/search", json={"query": "trailing"})
        item = resp.json()[0]
        assert "trailing vine" in item["description"]

    def test_search_uses_plant_id_as_slug_fallback(self, search_client):
        client, qdrant, *_ = search_client
        # payload has plant_id but no slug
        qdrant.search_dense_sparse.return_value = [
            {
                "score": 0.8,
                "payload": {"plant_id": "fallback-id", "plant_name": "Fallback Plant"},
            }
        ]
        resp = client.post("/search", json={"query": "fallback"})
        assert resp.status_code == 200
        data = resp.json()
        assert data[0]["slug"] == "fallback-id"
