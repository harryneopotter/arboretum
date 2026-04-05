"""
Beta/dev telemetry endpoints.

The app posts lightweight action + response summaries here during beta testing.
Admins can later inspect the stored events without needing user auth.
"""

import json
from typing import Optional

from fastapi import APIRouter, Header, HTTPException, status

from app.config import get_settings
from app.database import get_db
from app.models import TelemetryEventIn, TelemetryEventOut

router = APIRouter(prefix="/events", tags=["Telemetry"])


def _loads_json(value):
    if value in (None, "", "null"):
        return None
    try:
        return json.loads(value)
    except Exception:
        return None


def _assert_admin_token(x_admin_token: Optional[str]) -> None:
    settings = get_settings()
    if not settings.admin_log_token:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Admin telemetry access is not configured",
        )
    if x_admin_token != settings.admin_log_token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid admin token",
        )


@router.post("")
def log_event(event: TelemetryEventIn):
    settings = get_settings()
    if not settings.beta_telemetry_enabled:
        return {"status": "disabled"}

    with get_db() as conn:
        conn.execute(
            """
            INSERT INTO telemetry_events (
                device_id, session_id, screen, action, target, status, source,
                request_json, response_json, error_text
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                event.device_id,
                event.session_id,
                event.screen,
                event.action,
                event.target,
                event.status,
                event.source or "frontend",
                json.dumps(event.request_data) if event.request_data is not None else None,
                json.dumps(event.response_data) if event.response_data is not None else None,
                event.error_text,
            ),
        )
    return {"status": "ok"}


@router.get("/admin", response_model=list[TelemetryEventOut])
def list_events(
    limit: int = 100,
    device_id: Optional[str] = None,
    action: Optional[str] = None,
    screen: Optional[str] = None,
    status: Optional[str] = None,
    source: Optional[str] = None,
    x_admin_token: Optional[str] = Header(default=None, alias="X-Admin-Token"),
):
    settings = get_settings()
    if not settings.beta_telemetry_enabled:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Telemetry is disabled",
        )
    _assert_admin_token(x_admin_token)
    limit = max(1, min(limit, 500))
    query = """
        SELECT id, device_id, session_id, screen, action, target, status, source,
               request_json, response_json, error_text, created_at
        FROM telemetry_events
    """
    clauses = []
    params: list[object] = []

    if device_id:
        clauses.append("device_id = ?")
        params.append(device_id)
    if action:
        clauses.append("action = ?")
        params.append(action)
    if screen:
        clauses.append("screen = ?")
        params.append(screen)
    if status:
        clauses.append("status = ?")
        params.append(status)
    if source:
        clauses.append("source = ?")
        params.append(source)

    if clauses:
        query += " WHERE " + " AND ".join(clauses)

    query += " ORDER BY created_at DESC LIMIT ?"
    params.append(limit)

    with get_db() as conn:
        rows = conn.execute(query, tuple(params)).fetchall()

    events: list[TelemetryEventOut] = []
    for row in rows:
        record = dict(row)
        record["request_data"] = _loads_json(record.pop("request_json", None))
        record["response_data"] = _loads_json(record.pop("response_json", None))
        events.append(TelemetryEventOut(**record))
    return events
