"""
Tests for the /user/* endpoints.
All DB operations use the temp SQLite injected by conftest.py.
"""

import json
import pytest
from fastapi.testclient import TestClient


class TestGetProfile:
    def test_returns_empty_profile_for_new_device(self, client):
        resp = client.get("/user/new-device-001/profile")
        assert resp.status_code == 200
        data = resp.json()
        assert data["device_id"] == "new-device-001"
        assert data["name"] == ""
        assert data["email"] == ""
        assert data["location"] == ""
        assert data["bio"] == ""
        assert data["avatar_url"] == ""

    def test_returns_saved_profile(self, client):
        client.put("/user/dev-abc/profile", json={"name": "Alice", "email": "alice@example.com"})
        resp = client.get("/user/dev-abc/profile")
        assert resp.status_code == 200
        data = resp.json()
        assert data["name"] == "Alice"
        assert data["email"] == "alice@example.com"


class TestUpdateProfile:
    def test_create_new_profile(self, client):
        resp = client.put(
            "/user/dev-001/profile",
            json={"name": "Bob", "email": "bob@test.com", "location": "Delhi"},
        )
        assert resp.status_code == 200
        assert resp.json() == {"status": "ok"}

    def test_update_existing_profile(self, client):
        client.put("/user/dev-002/profile", json={"name": "First"})
        client.put("/user/dev-002/profile", json={"name": "Updated"})
        resp = client.get("/user/dev-002/profile")
        assert resp.json()["name"] == "Updated"

    def test_partial_update_nulls_become_empty_string(self, client):
        # ProfileIn: all fields Optional, default None → stored as ""
        resp = client.put("/user/dev-003/profile", json={"name": "Test"})
        assert resp.status_code == 200
        profile = client.get("/user/dev-003/profile").json()
        assert profile["name"] == "Test"
        assert profile["email"] == ""  # not provided → empty string

    def test_all_fields_saved(self, client):
        payload = {
            "name": "Charlie",
            "email": "charlie@ex.com",
            "location": "Mumbai",
            "bio": "Loves plants",
            "avatar_url": "https://example.com/avatar.jpg",
        }
        client.put("/user/dev-004/profile", json=payload)
        profile = client.get("/user/dev-004/profile").json()
        for k, v in payload.items():
            assert profile[k] == v

    def test_upsert_preserves_device_id(self, client):
        client.put("/user/dev-005/profile", json={"name": "Original"})
        client.put("/user/dev-005/profile", json={"name": "Changed"})
        profile = client.get("/user/dev-005/profile").json()
        assert profile["device_id"] == "dev-005"


class TestSavedPlants:
    def test_empty_saved_list_for_new_device(self, client):
        resp = client.get("/user/dev-100/saved")
        assert resp.status_code == 200
        assert resp.json() == []

    def test_save_plant(self, client):
        resp = client.post("/user/dev-101/saved/money-plant")
        assert resp.status_code == 200
        assert resp.json() == {"status": "ok"}

    def test_saved_plant_appears_in_list(self, client):
        client.post("/user/dev-102/saved/aloe-vera")
        resp = client.get("/user/dev-102/saved")
        assert resp.status_code == 200
        assert "aloe-vera" in resp.json()

    def test_save_multiple_plants(self, client):
        for plant in ["fern", "cactus", "pothos"]:
            client.post(f"/user/dev-103/saved/{plant}")
        resp = client.get("/user/dev-103/saved")
        assert len(resp.json()) == 3

    def test_save_duplicate_plant_ignored(self, client):
        for _ in range(3):
            client.post("/user/dev-104/saved/fern")
        resp = client.get("/user/dev-104/saved")
        assert len(resp.json()) == 1

    def test_remove_saved_plant(self, client):
        client.post("/user/dev-105/saved/cactus")
        client.delete("/user/dev-105/saved/cactus")
        resp = client.get("/user/dev-105/saved")
        assert "cactus" not in resp.json()

    def test_remove_nonexistent_plant_is_safe(self, client):
        resp = client.delete("/user/dev-106/saved/nonexistent")
        assert resp.status_code == 200

    def test_saved_plants_are_device_isolated(self, client):
        client.post("/user/dev-107/saved/shared-plant")
        resp_108 = client.get("/user/dev-108/saved")
        assert "shared-plant" not in resp_108.json()


class TestDiagnosisHistory:
    def test_empty_history_for_new_device(self, client):
        resp = client.get("/user/dev-200/history")
        assert resp.status_code == 200
        assert resp.json() == []

    def test_add_history_entry(self, client):
        entry = {
            "plant_id": "money-plant",
            "plant_name": "Money Plant",
            "symptom": "Yellow leaves",
            "result": {"fix": "Reduce watering"},
        }
        resp = client.post("/user/dev-201/history", json=entry)
        assert resp.status_code == 200
        assert resp.json() == {"status": "ok"}

    def test_history_entry_retrievable(self, client):
        entry = {
            "plant_id": "aloe-vera",
            "plant_name": "Aloe Vera",
            "symptom": "Brown tips",
            "result": None,
        }
        client.post("/user/dev-202/history", json=entry)
        history = client.get("/user/dev-202/history").json()
        assert len(history) == 1
        assert history[0]["plant_name"] == "Aloe Vera"
        assert history[0]["symptom"] == "Brown tips"

    def test_history_result_json_deserialized(self, client):
        entry = {
            "plant_id": "fern",
            "plant_name": "Fern",
            "symptom": "Wilting",
            "result": {"symptom": "Wilting", "fix": "Water immediately"},
        }
        client.post("/user/dev-203/history", json=entry)
        history = client.get("/user/dev-203/history").json()
        assert history[0]["result"]["fix"] == "Water immediately"

    def test_history_no_result_json_handled(self, client):
        entry = {"plant_id": "cactus", "plant_name": "Cactus", "symptom": "Dry", "result": None}
        client.post("/user/dev-204/history", json=entry)
        history = client.get("/user/dev-204/history").json()
        # result_json was None, so 'result' key may not be present
        assert history[0]["symptom"] == "Dry"

    def test_history_ordered_most_recent_first(self, client):
        for symptom in ["first", "second", "third"]:
            client.post("/user/dev-205/history", json={"symptom": symptom, "result": None})
        history = client.get("/user/dev-205/history").json()
        assert history[0]["symptom"] == "third"

    def test_history_limit_parameter(self, client):
        for i in range(10):
            client.post("/user/dev-206/history", json={"symptom": f"symptom-{i}", "result": None})
        history = client.get("/user/dev-206/history?limit=3").json()
        assert len(history) == 3

    def test_history_default_limit_20(self, client):
        for i in range(25):
            client.post("/user/dev-207/history", json={"symptom": f"symptom-{i}", "result": None})
        history = client.get("/user/dev-207/history").json()
        assert len(history) == 20

    def test_history_device_isolated(self, client):
        client.post("/user/dev-208/history", json={"symptom": "test", "result": None})
        history_209 = client.get("/user/dev-209/history").json()
        assert len(history_209) == 0
