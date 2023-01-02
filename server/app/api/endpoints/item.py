from fastapi import APIRouter, Depends

from app.models import Item
from app.db import Session
from app.deps import get_db


router = APIRouter()


@router.post('/')
def item_create(*, db: Session = Depends(get_db)) -> Item:
    return Item.crud.create(db)


@router.get('/{id}/')
def item_get(*, id: int, db: Session = Depends(get_db)) -> Item:
    # experiment()
    return Item.crud.get_or_404(db, id=id)


DBG = '''
def exp_f(obj_in: int) -> None:
    print(obj_in, type(obj_in))


def experiment() -> None:
    exp_f('a')
'''
