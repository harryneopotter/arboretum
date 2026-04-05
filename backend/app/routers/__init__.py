from .identify import router as identify_router
from .search import router as search_router
from .diagnose import router as diagnose_router
from .plant import router as plant_router
from .user import router as user_router
from .telemetry import router as telemetry_router

__all__ = ["identify_router", "search_router", "diagnose_router", "plant_router", "user_router", "telemetry_router"]
