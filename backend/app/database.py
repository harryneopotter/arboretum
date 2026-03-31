"""
SQLite persistence layer for user profiles, saved plants, and diagnosis history.
DB file is stored at backend/arboretum.db (gitignored).
"""

import sqlite3
from contextlib import contextmanager
from pathlib import Path

DB_PATH = Path(__file__).parent.parent / "arboretum.db"


@contextmanager
def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    try:
        yield conn
        conn.commit()
    finally:
        conn.close()


def init_db():
    with get_db() as conn:
        conn.executescript("""
            CREATE TABLE IF NOT EXISTS profiles (
                device_id  TEXT PRIMARY KEY,
                name       TEXT DEFAULT '',
                email      TEXT DEFAULT '',
                location   TEXT DEFAULT '',
                bio        TEXT DEFAULT '',
                avatar_url TEXT DEFAULT '',
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );

            CREATE TABLE IF NOT EXISTS saved_plants (
                device_id TEXT NOT NULL,
                plant_id  TEXT NOT NULL,
                saved_at  TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                PRIMARY KEY (device_id, plant_id)
            );

            CREATE TABLE IF NOT EXISTS diagnosis_history (
                id          INTEGER PRIMARY KEY AUTOINCREMENT,
                device_id   TEXT NOT NULL,
                plant_id    TEXT,
                plant_name  TEXT,
                symptom     TEXT,
                result_json TEXT,
                created_at  TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
        """)
