"""
Plant Care FastAPI Backend - Main Application

Run with: uvicorn app.main:app --reload
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from app.routers import (
    identify_router,
    search_router,
    diagnose_router,
    plant_router,
    user_router,
    telemetry_router,
)
from app.config import get_settings

# =============================================================================
# App Initialization
# =============================================================================

settings = get_settings()

app = FastAPI(
    title="Plant Care API",
    description="Backend API for plant identification, search, and diagnosis",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)


@app.on_event("startup")
async def startup_event():
    # Keep startup lightweight for Cloud Run. Database schema creation and
    # model loading happen lazily on the first request that needs them.
    return


# =============================================================================
# CORS Middleware (Android-friendly)
# =============================================================================

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# =============================================================================
# Routers
# =============================================================================

app.include_router(identify_router)
app.include_router(search_router)
app.include_router(diagnose_router)
app.include_router(plant_router)
app.include_router(user_router)
app.include_router(telemetry_router)

# =============================================================================
# Static Files
# =============================================================================

app.mount("/static", StaticFiles(directory="app/static"), name="static")

# =============================================================================
# Health Check
# =============================================================================


@app.get("/health", tags=["Health"])
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "qdrant_url": settings.qdrant_url,
        "plants_collection": settings.plants_collection,
        "plant_images_collection": settings.plant_images_collection,
    }


# =============================================================================
# Root Endpoint
# =============================================================================


@app.get("/", tags=["Root"])
async def root():
    """Root endpoint with API info."""
    return {
        "name": "Plant Care API",
        "version": "1.0.0",
        "docs": "/docs",
        "endpoints": {
            "identify": "/identify",
            "search": "/search",
            "diagnose": "/diagnose",
            "events": "/events",
            "plant": "/plant/{id}",
        },
    }
