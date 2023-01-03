from typing import Optional
from sqlmodel import Field
from app.db import BaseModel, BaseCRUD


class CRUD(BaseCRUD['Item']):
    pass

class BaseItem(BaseModel):
    pass

class Item(BaseItem, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)


class ItemRead(BaseItem):
    id: int


class ItemCreate(BaseItem):
    pass


Item.crud = CRUD(Item)
