from fastapi import APIRouter, Depends

from app.models import Item
from app.db import Session
from app.deps import get_db


router = APIRouter()


@router.post('/')
async def item_create(*, db: Session = Depends(get_db)):
    return await Item.objects.create()


@router.get('/{id}/')
async def item_get(*, id: int, db: Session = Depends(get_db)):
    return await Item.objects.get(id=id)
