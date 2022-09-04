from fastapi import APIRouter, Depends

from app.models import Item
from app.db import Session
from app.deps import get_db


router = APIRouter()


@router.post('/')
async def item_create(*, db: Session = Depends(get_db)) -> Item:
    return await Item.crud.create(db)


@router.get('/{id}/')
async def item_get(*, id: int, db: Session = Depends(get_db)) -> Item:
    # experiment()
    return await Item.crud.get(db, id=id)


DBG = '''
def exp_f(obj_in: int) -> None:
    print(obj_in, type(obj_in))


def experiment() -> None:
    exp_f('a')
'''
