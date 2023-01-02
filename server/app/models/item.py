from typing import Optional
from sqlmodel import Field
from app.db import BaseModel, BaseCRUD


class CRUD(BaseCRUD['Item']):
    pass


class Item(BaseModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)

Item.crud = CRUD(Item)
