"""
User persistence endpoints: profile, saved plants, diagnosis history.
All routes are keyed by device_id (a UUID generated client-side on first run).
"""

import json
from typing import Optional

from fastapi import APIRouter
from pydantic import BaseModel

from app.database import get_db

router = APIRouter(prefix="/user", tags=["User"])


# ---------------------------------------------------------------------------
# Request models
# ---------------------------------------------------------------------------

class ProfileIn(BaseModel):
    name: Optional[str] = None
    email: Optional[str] = None
    location: Optional[str] = None
    bio: Optional[str] = None
    avatar_url: Optional[str] = None


class HistoryEntry(BaseModel):
    plant_id: Optional[str] = None
    plant_name: Optional[str] = None
    symptom: str
    result: Optional[dict] = None


# ---------------------------------------------------------------------------
# Profile
# ---------------------------------------------------------------------------

@router.get("/{device_id}/profile")
def get_profile(device_id: str):
    with get_db() as conn:
        row = conn.execute(
            "SELECT * FROM profiles WHERE device_id = ?", (device_id,)
        ).fetchone()
    if not row:
        return {"device_id": device_id, "name": "", "email": "", "location": "", "bio": "", "avatar_url": ""}
    return dict(row)


@router.put("/{device_id}/profile")
def update_profile(device_id: str, profile: ProfileIn):
    with get_db() as conn:
        conn.execute(
            """
            INSERT INTO profiles (device_id, name, email, location, bio, avatar_url, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
            ON CONFLICT(device_id) DO UPDATE SET
                name       = excluded.name,
                email      = excluded.email,
                location   = excluded.location,
                bio        = excluded.bio,
                avatar_url = excluded.avatar_url,
                updated_at = CURRENT_TIMESTAMP
            """,
            (
                device_id,
                profile.name or "",
                profile.email or "",
                profile.location or "",
                profile.bio or "",
                profile.avatar_url or "",
            ),
        )
    return {"status": "ok"}


# ---------------------------------------------------------------------------
# Saved plants
# ---------------------------------------------------------------------------

@router.get("/{device_id}/saved")
def get_saved(device_id: str):
    with get_db() as conn:
        rows = conn.execute(
            "SELECT plant_id FROM saved_plants WHERE device_id = ? ORDER BY saved_at DESC",
            (device_id,),
        ).fetchall()
    return [row["plant_id"] for row in rows]


@router.post("/{device_id}/saved/{plant_id}")
def save_plant(device_id: str, plant_id: str):
    with get_db() as conn:
        conn.execute(
            "INSERT OR IGNORE INTO saved_plants (device_id, plant_id) VALUES (?, ?)",
            (device_id, plant_id),
        )
    return {"status": "ok"}


@router.delete("/{device_id}/saved/{plant_id}")
def remove_plant(device_id: str, plant_id: str):
    with get_db() as conn:
        conn.execute(
            "DELETE FROM saved_plants WHERE device_id = ? AND plant_id = ?",
            (device_id, plant_id),
        )
    return {"status": "ok"}


# ---------------------------------------------------------------------------
# Diagnosis history
# ---------------------------------------------------------------------------

@router.get("/{device_id}/history")
def get_history(device_id: str, limit: int = 20):
    with get_db() as conn:
        rows = conn.execute(
            """
            SELECT id, plant_id, plant_name, symptom, result_json, created_at
            FROM diagnosis_history
            WHERE device_id = ?
            ORDER BY created_at DESC
            LIMIT ?
            """,
            (device_id, limit),
        ).fetchall()
    result = []
    for row in rows:
        entry = dict(row)
        if entry["result_json"]:
            entry["result"] = json.loads(entry["result_json"])
        del entry["result_json"]
        result.append(entry)
    return result


@router.post("/{device_id}/history")
def add_history(device_id: str, entry: HistoryEntry):
    with get_db() as conn:
        conn.execute(
            """
            INSERT INTO diagnosis_history (device_id, plant_id, plant_name, symptom, result_json)
            VALUES (?, ?, ?, ?, ?)
            """,
            (
                device_id,
                entry.plant_id,
                entry.plant_name,
                entry.symptom,
                json.dumps(entry.result) if entry.result else None,
            ),
        )
    return {"status": "ok"}
