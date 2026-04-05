"""
Persistence layer for user profiles, saved plants, and diagnosis history.

Defaults to local SQLite for development. If Cloud SQL / Postgres settings are
provided, the same schema is created in PostgreSQL for Cloud Run or other
managed hosting.
"""

from contextlib import contextmanager
from pathlib import Path
import sqlite3

from app.config import get_settings

try:
    import psycopg
    from psycopg.rows import dict_row
except Exception:  # pragma: no cover - optional until requirements are installed
    psycopg = None
    dict_row = None

DB_PATH = Path(__file__).parent.parent / "arboretum.db"
_SCHEMA_INITIALIZED = False


def _is_postgres(database_url: str | None) -> bool:
    return bool(database_url) and database_url.startswith(("postgres://", "postgresql://"))


def _has_postgres_settings(settings) -> bool:
    return bool(settings.db_user and settings.db_name and settings.db_host)


def _normalize_sql(query: str, postgres: bool) -> str:
    return query.replace("?", "%s") if postgres else query


class DatabaseConnection:
    def __init__(self, conn, postgres: bool):
        self.conn = conn
        self.postgres = postgres

    def execute(self, query: str, params: tuple = ()):
        cursor = self.conn.cursor()
        cursor.execute(_normalize_sql(query, self.postgres), params)
        return cursor

    def executemany(self, query: str, seq_of_params):
        cursor = self.conn.cursor()
        cursor.executemany(_normalize_sql(query, self.postgres), seq_of_params)
        return cursor

    def executescript(self, script: str):
        statements = [stmt.strip() for stmt in script.split(";") if stmt.strip()]
        cursor = None
        for statement in statements:
            cursor = self.execute(statement)
        return cursor

    def commit(self):
        self.conn.commit()

    def rollback(self):
        self.conn.rollback()

    def close(self):
        self.conn.close()


def _create_connection():
    settings = get_settings()
    database_url = settings.database_url

    if _is_postgres(database_url):
        if psycopg is None:
            raise RuntimeError("psycopg is required when DATABASE_URL points to PostgreSQL")
        conn = psycopg.connect(database_url, row_factory=dict_row)
        return DatabaseConnection(conn, postgres=True)

    if _has_postgres_settings(settings):
        if psycopg is None:
            raise RuntimeError("psycopg is required when DB_* settings point to PostgreSQL")
        conn = psycopg.connect(
            dbname=settings.db_name,
            user=settings.db_user,
            password=settings.db_pass or "",
            host=settings.db_host,
            row_factory=dict_row,
        )
        return DatabaseConnection(conn, postgres=True)

    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return DatabaseConnection(conn, postgres=False)


@contextmanager
def get_db():
    global _SCHEMA_INITIALIZED
    conn = _create_connection()
    try:
        if not _SCHEMA_INITIALIZED:
            settings = get_settings()
            schema = POSTGRES_SCHEMA if (_is_postgres(settings.database_url) or _has_postgres_settings(settings)) else SQLITE_SCHEMA
            conn.executescript(schema)
            _SCHEMA_INITIALIZED = True
        yield conn
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


SQLITE_SCHEMA = """
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

    CREATE TABLE IF NOT EXISTS telemetry_events (
        id              INTEGER PRIMARY KEY AUTOINCREMENT,
        device_id       TEXT,
        session_id      TEXT,
        screen          TEXT,
        action          TEXT NOT NULL,
        target          TEXT,
        status          TEXT,
        source          TEXT DEFAULT 'frontend',
        request_json    TEXT,
        response_json   TEXT,
        error_text      TEXT,
        created_at      TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
"""

POSTGRES_SCHEMA = """
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
        id          BIGSERIAL PRIMARY KEY,
        device_id   TEXT NOT NULL,
        plant_id    TEXT,
        plant_name  TEXT,
        symptom     TEXT,
        result_json TEXT,
        created_at  TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );

    CREATE TABLE IF NOT EXISTS telemetry_events (
        id              BIGSERIAL PRIMARY KEY,
        device_id       TEXT,
        session_id      TEXT,
        screen          TEXT,
        action          TEXT NOT NULL,
        target          TEXT,
        status          TEXT,
        source          TEXT DEFAULT 'frontend',
        request_json    TEXT,
        response_json   TEXT,
        error_text      TEXT,
        created_at      TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
"""


def init_db():
    global _SCHEMA_INITIALIZED
    with get_db() as conn:
        settings = get_settings()
        schema = POSTGRES_SCHEMA if (_is_postgres(settings.database_url) or _has_postgres_settings(settings)) else SQLITE_SCHEMA
        conn.executescript(schema)
        _SCHEMA_INITIALIZED = True
