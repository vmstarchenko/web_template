from sqlalchemy import Column, Integer

from app.db import Base


class Item(Base):
    id = Column(Integer, primary_key=True, autoincrement=True)
