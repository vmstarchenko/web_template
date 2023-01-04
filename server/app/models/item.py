from typing import Optional
from sqlmodel import Field
from app.db import BaseModel, BaseCRUD

__all__ = ('Item', 'ItemRead', 'ItemCreate',)


class CRUD(BaseCRUD['Item']):
    pass

class BaseItem(BaseModel):
    pass


class Item(BaseItem, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)

    crud: CRUD = CRUD.default()

Item.crud = CRUD(Item)

class ItemRead(BaseItem):
    id: int


class ItemCreate(BaseItem):
    pass
