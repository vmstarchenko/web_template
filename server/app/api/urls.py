from fastapi import APIRouter

from app.core import settings

from .endpoints import (
    common, item
)


api_router = APIRouter()
api_router.include_router(item.router, prefix='/item')

router = APIRouter()
router.include_router(common.router)
router.include_router(api_router, prefix=settings.API_PREFIX)
