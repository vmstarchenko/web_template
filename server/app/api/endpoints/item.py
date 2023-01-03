from fastapi import APIRouter, Depends

from app.models import Item, ItemRead, ItemCreate
from app.db import Session
from app.deps import get_db


router = APIRouter()


@router.post('/', response_model=ItemRead)
async def item_create(*, db: Session = Depends(get_db)) -> Item:
    return await Item.crud.create(db)


@router.get('/{id}/', response_model=ItemRead)
async def item_get(*, id: int, db: Session = Depends(get_db)) -> Item:
    # experiment()
    return await Item.crud.get_or_404(db, id=id)


DBG = '''
def exp_f(obj_in: int) -> None:
    print(obj_in, type(obj_in))


def experiment() -> None:
    exp_f('a')
'''
