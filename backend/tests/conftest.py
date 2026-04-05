"""
Shared fixtures for all tests.
"""

import sqlite3
import pytest
from pathlib import Path
from fastapi.testclient import TestClient


@pytest.fixture(autouse=True)
def use_temp_db(tmp_path, monkeypatch):
    """
    Redirect all database operations to a fresh temporary SQLite file.
    This runs before every test so each test gets a clean, isolated DB.
    """
    db_file = tmp_path / "test_arboretum.db"
    monkeypatch.setattr("app.database.DB_PATH", db_file)
    # Re-run init so the tables exist in the temp file
    from app.database import init_db
    init_db()
    yield db_file


@pytest.fixture
def client(use_temp_db):
    """Return a synchronous FastAPI TestClient backed by the temp DB."""
    from app.main import app
    with TestClient(app) as c:
        yield c
