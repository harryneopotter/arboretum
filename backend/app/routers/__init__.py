from .identify import router as identify_router
from .search import router as search_router
from .diagnose import router as diagnose_router
from .plant import router as plant_router

__all__ = ["identify_router", "search_router", "diagnose_router", "plant_router"]
