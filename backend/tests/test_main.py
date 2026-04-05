"""
Tests for the root and health check endpoints.
"""

import pytest
from fastapi.testclient import TestClient


class TestHealthCheck:
    def test_health_returns_200(self, client):
        resp = client.get("/health")
        assert resp.status_code == 200

    def test_health_status_healthy(self, client):
        resp = client.get("/health")
        assert resp.json()["status"] == "healthy"

    def test_health_contains_qdrant_url(self, client):
        resp = client.get("/health")
        data = resp.json()
        assert "qdrant_url" in data
        assert data["qdrant_url"] != ""

    def test_health_contains_collections(self, client):
        resp = client.get("/health")
        data = resp.json()
        assert "plants_collection" in data
        assert "plant_images_collection" in data
        assert data["plants_collection"] == "plants"
        assert data["plant_images_collection"] == "plant-images"


class TestRootEndpoint:
    def test_root_returns_200(self, client):
        resp = client.get("/")
        assert resp.status_code == 200

    def test_root_name(self, client):
        resp = client.get("/")
        assert resp.json()["name"] == "Plant Care API"

    def test_root_version(self, client):
        resp = client.get("/")
        assert resp.json()["version"] == "1.0.0"

    def test_root_contains_docs_link(self, client):
        resp = client.get("/")
        assert resp.json()["docs"] == "/docs"

    def test_root_endpoints_map(self, client):
        resp = client.get("/")
        endpoints = resp.json()["endpoints"]
        assert "identify" in endpoints
        assert "search" in endpoints
        assert "diagnose" in endpoints
        assert "plant" in endpoints
