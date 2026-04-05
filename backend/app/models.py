"""
Pydantic models for request/response schemas.
"""

from datetime import datetime

from pydantic import BaseModel, Field
from typing import Optional


# =============================================================================
# Request Models
# =============================================================================


class IdentifyRequest(BaseModel):
    """Request body for image identification."""
    image: str = Field(..., description="Base64-encoded image string")


class SearchRequest(BaseModel):
    """Request body for text search."""
    query: str = Field(..., min_length=1, max_length=1000, description="Search query text")
    limit: int = Field(default=5, ge=1, le=20, description="Maximum number of results")


class DiagnoseRequest(BaseModel):
    """Request body for plant diagnosis."""
    plant_id: str = Field(..., description="Plant identifier (e.g., 'plant:money_plant')")
    symptom: str = Field(..., min_length=1, max_length=500, description="Observed symptom description")


# =============================================================================
# Response Models
# =============================================================================


class PlantMatch(BaseModel):
    """A plant match result."""
    slug: str
    plant_name: str
    score: float


class IdentifyMatch(PlantMatch):
    """Image identification match."""
    image_url: Optional[str] = None


class IdentifyResponse(BaseModel):
    """Response for image identification."""
    matches: list[IdentifyMatch]
    plant: Optional[dict] = None
    message: Optional[str] = None


class SearchResponseItem(BaseModel):
    """Single search result item."""
    slug: Optional[str] = ""
    plant_name: str
    score: float
    category: Optional[str] = None
    description: Optional[str] = None


class ProblemEntry(BaseModel):
    """Plant problem/issue entry."""
    symptom: str
    possible_causes: list[str]
    fix: str
    prevention: str


class DiagnoseResponse(BaseModel):
    """Response for diagnosis endpoint."""
    problem: Optional[ProblemEntry] = None
    message: Optional[str] = None


class TelemetryEventIn(BaseModel):
    """Beta/dev telemetry event captured from the app."""
    device_id: Optional[str] = None
    session_id: Optional[str] = None
    screen: Optional[str] = None
    action: str = Field(..., min_length=1, max_length=120)
    target: Optional[str] = None
    status: Optional[str] = None
    source: Optional[str] = Field(default="frontend")
    request_data: Optional[dict] = None
    response_data: Optional[dict] = None
    error_text: Optional[str] = None


class TelemetryEventOut(BaseModel):
    """Stored telemetry event."""
    id: int
    device_id: Optional[str] = None
    session_id: Optional[str] = None
    screen: Optional[str] = None
    action: str
    target: Optional[str] = None
    status: Optional[str] = None
    source: Optional[str] = None
    request_data: Optional[dict] = None
    response_data: Optional[dict] = None
    error_text: Optional[str] = None
    created_at: Optional[datetime] = None


class PlantResponse(BaseModel):
    """Full plant profile response."""
    plant_name: str
    alternate_names: list[str]
    category: str
    description: str
    care: dict
    common_problems: list[dict]
    reference_images: list[dict]

    class Config:
        extra = "allow"


class ErrorResponse(BaseModel):
    """Error response model."""
    detail: str
