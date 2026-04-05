"""
Tests for GET /plant/{plant_id} endpoint.
Qdrant service is mocked to avoid network access.
"""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from fastapi.testclient import TestClient


PLANT_PAYLOAD = {
    "slug": "money-plant",
    "plant_id": "plant:money_plant",
    "plant_name": "Money Plant",
    "category": "Indoor",
    "description": "A popular trailing vine.",
    "care": {"watering_frequency": "Weekly"},
    "common_problems": [
        {
            "symptom": "Yellow leaves",
            "possible_causes": ["Overwatering"],
            "fix": "Reduce watering.",
            "prevention": "Ensure drainage.",
        }
    ],
    "alternate_names": ["Golden Pothos"],
    "reference_images": [],
}


@pytest.fixture
def mock_qdrant():
    m = MagicMock()
    m.scroll_points = AsyncMock(return_value=[])
    return m


@pytest.fixture
def plant_client(mock_qdrant, use_temp_db):
    with patch("app.routers.plant.get_qdrant", return_value=mock_qdrant):
        from app.main import app
        with TestClient(app) as c:
            yield c, mock_qdrant


class TestGetPlantProfile:
    def test_found_by_slug(self, plant_client):
        client, qdrant = plant_client
        qdrant.scroll_points.side_effect = [
            [{"payload": PLANT_PAYLOAD}],  # first call: slug match
        ]
        resp = client.get("/plant/money-plant")
        assert resp.status_code == 200
        data = resp.json()
        assert data["plant_name"] == "Money Plant"

    def test_fallback_to_plant_id(self, plant_client):
        client, qdrant = plant_client
        # First scroll (slug) returns nothing; second (plant_id) returns result
        qdrant.scroll_points.side_effect = [
            [],  # slug not found
            [{"payload": PLANT_PAYLOAD}],  # plant_id found
        ]
        resp = client.get("/plant/plant:money_plant")
        assert resp.status_code == 200
        assert resp.json()["plant_name"] == "Money Plant"

    def test_not_found_returns_404(self, plant_client):
        client, qdrant = plant_client
        qdrant.scroll_points.side_effect = [[], []]  # both searches fail
        resp = client.get("/plant/nonexistent-plant")
        assert resp.status_code == 404
        assert "not found" in resp.json()["detail"].lower()

    def test_response_includes_care(self, plant_client):
        client, qdrant = plant_client
        qdrant.scroll_points.side_effect = [[{"payload": PLANT_PAYLOAD}]]
        resp = client.get("/plant/money-plant")
        assert "care" in resp.json()
        assert resp.json()["care"]["watering_frequency"] == "Weekly"

    def test_response_includes_problems(self, plant_client):
        client, qdrant = plant_client
        qdrant.scroll_points.side_effect = [[{"payload": PLANT_PAYLOAD}]]
        resp = client.get("/plant/money-plant")
        problems = resp.json()["common_problems"]
        assert len(problems) == 1
        assert problems[0]["symptom"] == "Yellow leaves"

    def test_qdrant_exception_returns_500(self, plant_client):
        client, qdrant = plant_client
        qdrant.scroll_points.side_effect = Exception("Qdrant error")
        resp = client.get("/plant/money-plant")
        assert resp.status_code == 500
        assert "Failed to retrieve plant" in resp.json()["detail"]

    def test_enrich_payload_fills_missing_description(self, plant_client):
        """If description is missing but text_blob is present, enrich_payload fills it."""
        client, qdrant = plant_client
        payload_with_blob = {
            "slug": "fern",
            "plant_name": "Fern",
            "category": "Outdoor",
            "text_blob": "Description: A beautiful fern.\nCare Instructions:\n- Watering Frequency: Daily",
            # No 'description' field — enrich_payload should add it
        }
        qdrant.scroll_points.side_effect = [[{"payload": payload_with_blob}]]
        resp = client.get("/plant/fern")
        assert resp.status_code == 200
        data = resp.json()
        assert "fern" in data["description"].lower() or data["description"] != ""
