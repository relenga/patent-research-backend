from fastapi import APIRouter

from .health import router as health_router
from .posts import router as posts_router
from .tiers import router as tiers_router

router = APIRouter(prefix="/v1")
router.include_router(health_router)
router.include_router(posts_router)
router.include_router(tiers_router)
