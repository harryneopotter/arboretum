"""
Tests for POST /identify endpoint.
Image embedding and Qdrant services are mocked.
"""

import base64
import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from fastapi.testclient import TestClient


# A minimal valid 1x1 red PNG as base64
RED_PIXEL_PNG_B64 = (
    "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mP8"
    "z8BQDwADhQGAWjR9awAAAABJRU5ErkJggg=="
)


IMAGE_SEARCH_RESULTS_HIGH = [
    {"score": 0.85, "payload": {"plant_slug": "money-plant", "plant_name": "Money Plant", "image_url": "http://img.jpg"}},
    {"score": 0.71, "payload": {"plant_slug": "aloe-vera", "plant_name": "Aloe Vera", "image_url": None}},
    {"score": 0.60, "payload": {"slug": "fern", "plant_name": "Fern", "image_url": None}},
]

IMAGE_SEARCH_RESULTS_LOW = [
    {"score": 0.15, "payload": {"plant_slug": "unknown-plant", "plant_name": "Unknown", "image_url": None}},
]

PLANT_SCROLL_RESULT = [
    {
        "payload": {
            "slug": "money-plant",
            "plant_name": "Money Plant",
            "category": "Indoor",
            "description": "A popular plant.",
            "care": {"watering_frequency": "Weekly"},
            "common_problems": [],
            "alternate_names": [],
            "reference_images": [],
        }
    }
]


@pytest.fixture
def mock_image_svc():
    svc = MagicMock()
    svc.embed = AsyncMock(return_value=[0.1] * 512)
    return svc


@pytest.fixture
def mock_qdrant():
    q = MagicMock()
    q.search_image = AsyncMock(return_value=IMAGE_SEARCH_RESULTS_HIGH)
    q.scroll_points = AsyncMock(return_value=PLANT_SCROLL_RESULT)
    return q


@pytest.fixture
def identify_client(mock_image_svc, mock_qdrant, use_temp_db):
    with (
        patch("app.routers.identify.get_image_embedding", return_value=mock_image_svc),
        patch("app.routers.identify.get_qdrant", return_value=mock_qdrant),
    ):
        from app.main import app
        with TestClient(app) as c:
            yield c, mock_image_svc, mock_qdrant


class TestIdentifyEndpoint:
    def test_successful_identification(self, identify_client):
        client, *_ = identify_client
        resp = client.post("/identify", json={"image": RED_PIXEL_PNG_B64})
        assert resp.status_code == 200

    def test_response_contains_matches(self, identify_client):
        client, *_ = identify_client
        resp = client.post("/identify", json={"image": RED_PIXEL_PNG_B64})
        data = resp.json()
        assert "matches" in data
        assert len(data["matches"]) == 3

    def test_response_contains_plant_on_high_confidence(self, identify_client):
        client, *_ = identify_client
        resp = client.post("/identify", json={"image": RED_PIXEL_PNG_B64})
        data = resp.json()
        assert data["plant"] is not None
        assert data["plant"]["plant_name"] == "Money Plant"

    def test_matches_have_correct_fields(self, identify_client):
        client, *_ = identify_client
        resp = client.post("/identify", json={"image": RED_PIXEL_PNG_B64})
        match = resp.json()["matches"][0]
        assert "slug" in match
        assert "plant_name" in match
        assert "score" in match

    def test_best_match_slug_extracted(self, identify_client):
        client, *_ = identify_client
        resp = client.post("/identify", json={"image": RED_PIXEL_PNG_B64})
        assert resp.json()["matches"][0]["slug"] == "money-plant"

    def test_low_confidence_returns_no_plant(self, identify_client):
        client, _, qdrant = identify_client
        qdrant.search_image.return_value = IMAGE_SEARCH_RESULTS_LOW
        resp = client.post("/identify", json={"image": RED_PIXEL_PNG_B64})
        assert resp.status_code == 200
        data = resp.json()
        assert data["plant"] is None
        assert "Low confidence" in data["message"]

    def test_no_image_results_returns_empty(self, identify_client):
        client, _, qdrant = identify_client
        qdrant.search_image.return_value = []
        resp = client.post("/identify", json={"image": RED_PIXEL_PNG_B64})
        assert resp.status_code == 200
        data = resp.json()
        assert data["matches"] == []
        assert "No matches" in data["message"]

    def test_image_embedding_called(self, identify_client):
        client, image_svc, _ = identify_client
        client.post("/identify", json={"image": RED_PIXEL_PNG_B64})
        image_svc.embed.assert_called_once_with(RED_PIXEL_PNG_B64)

    def test_invalid_base64_returns_400(self, identify_client):
        client, image_svc, _ = identify_client
        # Make image embedding raise ValueError for invalid image
        image_svc.embed.side_effect = ValueError("Invalid image data")
        resp = client.post("/identify", json={"image": "NOT_VALID_BASE64!!!"})
        assert resp.status_code == 400
        assert "Invalid image data" in resp.json()["detail"]

    def test_qdrant_error_returns_500(self, identify_client):
        client, _, qdrant = identify_client
        qdrant.search_image.side_effect = Exception("Qdrant down")
        resp = client.post("/identify", json={"image": RED_PIXEL_PNG_B64})
        assert resp.status_code == 500
        assert "Identification failed" in resp.json()["detail"]

    def test_missing_image_field_rejected(self, identify_client):
        client, *_ = identify_client
        resp = client.post("/identify", json={})
        assert resp.status_code == 422

    def test_data_url_prefix_handled(self, identify_client):
        """Image data with 'data:image/png;base64,' prefix should be handled by the embed service."""
        client, image_svc, _ = identify_client
        image_with_prefix = f"data:image/png;base64,{RED_PIXEL_PNG_B64}"
        client.post("/identify", json={"image": image_with_prefix})
        # The router passes the raw image string to embed; embed handles the prefix
        image_svc.embed.assert_called_once_with(image_with_prefix)

    def test_plant_not_found_in_scroll_returns_none_plant(self, identify_client):
        client, _, qdrant = identify_client
        qdrant.scroll_points.return_value = []  # plant profile not found in plants collection
        resp = client.post("/identify", json={"image": RED_PIXEL_PNG_B64})
        assert resp.status_code == 200
        # matches still returned, but plant is None
        data = resp.json()
        assert data["plant"] is None
        assert len(data["matches"]) > 0

    def test_slug_falls_back_to_plant_name_slugify(self, identify_client):
        """If payload has no plant_slug or slug, falls back to slugify(plant_name)."""
        client, _, qdrant = identify_client
        qdrant.search_image.return_value = [
            {"score": 0.9, "payload": {"plant_name": "Chinese Evergreen"}}
        ]
        qdrant.scroll_points.return_value = []
        resp = client.post("/identify", json={"image": RED_PIXEL_PNG_B64})
        assert resp.status_code == 200
        # slug derived from plant_name
        assert resp.json()["matches"][0]["slug"] == "chinese-evergreen"
