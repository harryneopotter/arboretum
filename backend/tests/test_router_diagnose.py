"""
Tests for POST /diagnose endpoint.
Diagnosis service is mocked.
"""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from fastapi.testclient import TestClient


MOCK_DIAGNOSIS_RESULT = {
    "score": 0.6,
    "symptom": "Yellow leaves",
    "possible_causes": ["Overwatering", "Poor drainage"],
    "fix": "Reduce watering frequency.",
    "prevention": "Ensure the pot has drainage holes.",
}


@pytest.fixture
def mock_diagnosis_service():
    svc = MagicMock()
    svc.diagnose = AsyncMock(return_value=MOCK_DIAGNOSIS_RESULT)
    return svc


@pytest.fixture
def diagnose_client(mock_diagnosis_service, use_temp_db):
    with patch("app.routers.diagnose.get_diagnosis", return_value=mock_diagnosis_service):
        from app.main import app
        with TestClient(app) as c:
            yield c, mock_diagnosis_service


class TestDiagnoseEndpoint:
    def test_diagnosis_found(self, diagnose_client):
        client, _ = diagnose_client
        resp = client.post("/diagnose", json={
            "plant_id": "money-plant",
            "symptom": "Yellow leaves",
        })
        assert resp.status_code == 200
        data = resp.json()
        assert data["problem"] is not None
        assert data["problem"]["symptom"] == "Yellow leaves"

    def test_diagnosis_contains_causes(self, diagnose_client):
        client, _ = diagnose_client
        resp = client.post("/diagnose", json={
            "plant_id": "money-plant",
            "symptom": "Yellow leaves",
        })
        causes = resp.json()["problem"]["possible_causes"]
        assert "Overwatering" in causes

    def test_diagnosis_contains_fix(self, diagnose_client):
        client, _ = diagnose_client
        resp = client.post("/diagnose", json={"plant_id": "x", "symptom": "y"})
        assert "Reduce watering" in resp.json()["problem"]["fix"]

    def test_diagnosis_contains_prevention(self, diagnose_client):
        client, _ = diagnose_client
        resp = client.post("/diagnose", json={"plant_id": "x", "symptom": "y"})
        assert "drainage holes" in resp.json()["problem"]["prevention"]

    def test_no_match_returns_message(self, diagnose_client):
        client, svc = diagnose_client
        svc.diagnose.return_value = None
        resp = client.post("/diagnose", json={
            "plant_id": "money-plant",
            "symptom": "unknown symptom",
        })
        assert resp.status_code == 200
        data = resp.json()
        assert data["problem"] is None
        assert data["message"] is not None
        assert "No matching" in data["message"]

    def test_service_called_with_correct_args(self, diagnose_client):
        client, svc = diagnose_client
        client.post("/diagnose", json={
            "plant_id": "aloe-vera",
            "symptom": "brown tips",
        })
        svc.diagnose.assert_called_once_with(
            plant_id="aloe-vera",
            symptom="brown tips",
        )

    def test_missing_plant_id_rejected(self, diagnose_client):
        client, _ = diagnose_client
        resp = client.post("/diagnose", json={"symptom": "yellow leaves"})
        assert resp.status_code == 422

    def test_missing_symptom_rejected(self, diagnose_client):
        client, _ = diagnose_client
        resp = client.post("/diagnose", json={"plant_id": "money-plant"})
        assert resp.status_code == 422

    def test_empty_symptom_rejected(self, diagnose_client):
        client, _ = diagnose_client
        resp = client.post("/diagnose", json={"plant_id": "money-plant", "symptom": ""})
        assert resp.status_code == 422

    def test_symptom_too_long_rejected(self, diagnose_client):
        client, _ = diagnose_client
        resp = client.post("/diagnose", json={
            "plant_id": "x",
            "symptom": "y" * 501,
        })
        assert resp.status_code == 422

    def test_service_exception_returns_500(self, diagnose_client):
        client, svc = diagnose_client
        svc.diagnose.side_effect = Exception("Unexpected error")
        resp = client.post("/diagnose", json={"plant_id": "x", "symptom": "test"})
        assert resp.status_code == 500
        assert "Diagnosis failed" in resp.json()["detail"]

    def test_response_message_none_when_found(self, diagnose_client):
        client, _ = diagnose_client
        resp = client.post("/diagnose", json={"plant_id": "x", "symptom": "yellow"})
        # When a result is found, message field is absent (None)
        data = resp.json()
        assert data["problem"] is not None
        assert data.get("message") is None
