from sqlalchemy import Column, Integer

from app.db import BaseModel, BaseCRUD


class CRUD(BaseCRUD['Item']):
    pass


class Item(BaseModel):
    id = Column(Integer, primary_key=True, autoincrement=True)

    crud: CRUD
