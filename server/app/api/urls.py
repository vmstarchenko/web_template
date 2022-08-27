from fastapi import APIRouter

from .endpoints import (
    common,
)

router = APIRouter()
router.include_router(common.router, prefix="")
