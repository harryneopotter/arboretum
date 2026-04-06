"""
Tests for app/database.py – SQLite CRUD operations.
Uses the temp DB injected by conftest.py.
"""

import json
import sqlite3
import pytest
from app.database import get_db


class TestProfileCRUD:
    def test_get_nonexistent_profile_returns_nothing(self):
        with get_db() as conn:
            row = conn.execute(
                "SELECT * FROM profiles WHERE device_id = ?", ("unknown-device",)
            ).fetchone()
        assert row is None

    def test_insert_profile(self):
        with get_db() as conn:
            conn.execute(
                """INSERT INTO profiles (device_id, name, email, location, bio, avatar_url)
                   VALUES (?, ?, ?, ?, ?, ?)""",
                ("device-1", "Alice", "alice@example.com", "London", "Plant lover", ""),
            )
        with get_db() as conn:
            row = conn.execute(
                "SELECT * FROM profiles WHERE device_id = ?", ("device-1",)
            ).fetchone()
        assert row is not None
        assert row["name"] == "Alice"
        assert row["email"] == "alice@example.com"

    def test_upsert_profile(self):
        with get_db() as conn:
            conn.execute(
                """INSERT INTO profiles (device_id, name, email) VALUES (?, ?, ?)
                   ON CONFLICT(device_id) DO UPDATE SET name=excluded.name""",
                ("device-2", "Bob", "bob@example.com"),
            )
        with get_db() as conn:
            conn.execute(
                """INSERT INTO profiles (device_id, name, email) VALUES (?, ?, ?)
                   ON CONFLICT(device_id) DO UPDATE SET name=excluded.name""",
                ("device-2", "Bobby", "bob@example.com"),
            )
        with get_db() as conn:
            row = conn.execute(
                "SELECT name FROM profiles WHERE device_id = ?", ("device-2",)
            ).fetchone()
        assert row["name"] == "Bobby"

    def test_profile_primary_key_uniqueness(self):
        with get_db() as conn:
            conn.execute(
                "INSERT INTO profiles (device_id, name) VALUES (?, ?)",
                ("device-3", "Charlie"),
            )
        with pytest.raises(sqlite3.IntegrityError):
            with get_db() as conn:
                conn.execute(
                    "INSERT INTO profiles (device_id, name) VALUES (?, ?)",
                    ("device-3", "Duplicate"),
                )


class TestSavedPlantsCRUD:
    def test_empty_saved_list(self):
        with get_db() as conn:
            rows = conn.execute(
                "SELECT plant_id FROM saved_plants WHERE device_id = ?", ("device-10",)
            ).fetchall()
        assert rows == []

    def test_save_plant(self):
        with get_db() as conn:
            conn.execute(
                "INSERT OR IGNORE INTO saved_plants (device_id, plant_id) VALUES (?, ?)",
                ("device-10", "money-plant"),
            )
        with get_db() as conn:
            rows = conn.execute(
                "SELECT plant_id FROM saved_plants WHERE device_id = ?", ("device-10",)
            ).fetchall()
        assert len(rows) == 1
        assert rows[0]["plant_id"] == "money-plant"

    def test_save_plant_duplicate_ignored(self):
        for _ in range(3):
            with get_db() as conn:
                conn.execute(
                    "INSERT OR IGNORE INTO saved_plants (device_id, plant_id) VALUES (?, ?)",
                    ("device-11", "aloe-vera"),
                )
        with get_db() as conn:
            count = conn.execute(
                "SELECT COUNT(*) as c FROM saved_plants WHERE device_id = ? AND plant_id = ?",
                ("device-11", "aloe-vera"),
            ).fetchone()["c"]
        assert count == 1

    def test_save_multiple_plants(self):
        for pid in ["plant-a", "plant-b", "plant-c"]:
            with get_db() as conn:
                conn.execute(
                    "INSERT OR IGNORE INTO saved_plants (device_id, plant_id) VALUES (?, ?)",
                    ("device-12", pid),
                )
        with get_db() as conn:
            rows = conn.execute(
                "SELECT plant_id FROM saved_plants WHERE device_id = ?", ("device-12",)
            ).fetchall()
        assert len(rows) == 3

    def test_remove_plant(self):
        with get_db() as conn:
            conn.execute(
                "INSERT OR IGNORE INTO saved_plants (device_id, plant_id) VALUES (?, ?)",
                ("device-13", "fern"),
            )
        with get_db() as conn:
            conn.execute(
                "DELETE FROM saved_plants WHERE device_id = ? AND plant_id = ?",
                ("device-13", "fern"),
            )
        with get_db() as conn:
            rows = conn.execute(
                "SELECT plant_id FROM saved_plants WHERE device_id = ?", ("device-13",)
            ).fetchall()
        assert rows == []

    def test_remove_nonexistent_plant_is_safe(self):
        with get_db() as conn:
            # Should not raise
            conn.execute(
                "DELETE FROM saved_plants WHERE device_id = ? AND plant_id = ?",
                ("device-99", "nonexistent"),
            )

    def test_composite_primary_key(self):
        """Same plant_id for different device_ids should both persist."""
        for device in ["device-20", "device-21"]:
            with get_db() as conn:
                conn.execute(
                    "INSERT OR IGNORE INTO saved_plants (device_id, plant_id) VALUES (?, ?)",
                    (device, "shared-plant"),
                )
        with get_db() as conn:
            count = conn.execute(
                "SELECT COUNT(*) as c FROM saved_plants WHERE plant_id = ?", ("shared-plant",)
            ).fetchone()["c"]
        assert count == 2


class TestDiagnosisHistoryCRUD:
    def test_empty_history(self):
        with get_db() as conn:
            rows = conn.execute(
                "SELECT * FROM diagnosis_history WHERE device_id = ?", ("device-30",)
            ).fetchall()
        assert rows == []

    def test_add_history_entry(self):
        result_data = {"symptom": "yellow leaves", "fix": "reduce watering"}
        with get_db() as conn:
            conn.execute(
                """INSERT INTO diagnosis_history (device_id, plant_id, plant_name, symptom, result_json)
                   VALUES (?, ?, ?, ?, ?)""",
                ("device-30", "money-plant", "Money Plant", "Yellow leaves", json.dumps(result_data)),
            )
        with get_db() as conn:
            row = conn.execute(
                "SELECT * FROM diagnosis_history WHERE device_id = ?", ("device-30",)
            ).fetchone()
        assert row is not None
        assert row["plant_name"] == "Money Plant"
        assert row["symptom"] == "Yellow leaves"
        stored = json.loads(row["result_json"])
        assert stored["fix"] == "reduce watering"

    def test_history_autoincrement_id(self):
        for i in range(3):
            with get_db() as conn:
                conn.execute(
                    "INSERT INTO diagnosis_history (device_id, symptom) VALUES (?, ?)",
                    ("device-31", f"symptom-{i}"),
                )
        with get_db() as conn:
            rows = conn.execute(
                "SELECT id FROM diagnosis_history WHERE device_id = ? ORDER BY id",
                ("device-31",),
            ).fetchall()
        ids = [r["id"] for r in rows]
        assert ids == sorted(ids)
        assert len(set(ids)) == 3  # all unique

    def test_history_null_result_json(self):
        with get_db() as conn:
            conn.execute(
                "INSERT INTO diagnosis_history (device_id, symptom, result_json) VALUES (?, ?, ?)",
                ("device-32", "dry soil", None),
            )
        with get_db() as conn:
            row = conn.execute(
                "SELECT result_json FROM diagnosis_history WHERE device_id = ?", ("device-32",)
            ).fetchone()
        assert row["result_json"] is None

    def test_history_ordering_by_created_at(self):
        for symptom in ["first", "second", "third"]:
            with get_db() as conn:
                conn.execute(
                    "INSERT INTO diagnosis_history (device_id, symptom) VALUES (?, ?)",
                    ("device-33", symptom),
                )
        with get_db() as conn:
            rows = conn.execute(
                """SELECT symptom FROM diagnosis_history WHERE device_id = ?
                   ORDER BY id DESC LIMIT 20""",
                ("device-33",),
            ).fetchall()
        symptoms = [r["symptom"] for r in rows]
        # Most recent insert (third) should come first when ordered by id DESC
        assert symptoms[0] == "third"
        assert symptoms[-1] == "first"

    def test_multiple_devices_isolated(self):
        for device in ["dev-A", "dev-B"]:
            with get_db() as conn:
                conn.execute(
                    "INSERT INTO diagnosis_history (device_id, symptom) VALUES (?, ?)",
                    (device, "test symptom"),
                )
        with get_db() as conn:
            count_a = conn.execute(
                "SELECT COUNT(*) as c FROM diagnosis_history WHERE device_id = ?", ("dev-A",)
            ).fetchone()["c"]
            count_b = conn.execute(
                "SELECT COUNT(*) as c FROM diagnosis_history WHERE device_id = ?", ("dev-B",)
            ).fetchone()["c"]
        assert count_a == 1
        assert count_b == 1
