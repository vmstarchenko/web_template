from fastapi import APIRouter, Depends

from app.models import Item
from app.db import Session
from app.deps import get_db

router = APIRouter()


@router.get('/')
async def item(*, db: Session = Depends(get_db)):
    obj = Item()
    db.add(obj)
    await obj.save(db)
    return {'id': obj.id}
