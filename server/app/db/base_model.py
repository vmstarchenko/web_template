from typing import Any
from sqlalchemy.ext.declarative import DeclarativeMeta, declarative_base

from . import deps

from .session import Session
from .crud import BaseCRUD


class BaseModelMeta(DeclarativeMeta):
    def __new__(cls, name, bases, attrs):
        # if attrs.get('__annotations__'):
        #     attrs['__annotations__']['crud'] = attrs['CRUD']

        if attrs.get('__tablename__', None) is None and not attrs.get('__abstract__', False):
            attrs['__tablename__'] = name.lower()

        obj = super().__new__(cls, name, bases, attrs)

        if not attrs.get('__abstract__', False):
            ann = attrs.get('__annotations__', {})
            for key, attr in ann.items():
                if isinstance(attr, type) and issubclass(attr, BaseCRUD):
                    setattr(obj, key, attr(obj))

        return obj


AbstractBaseModel = declarative_base(metaclass=BaseModelMeta)


class CRUD(BaseCRUD['BaseModel']):
    pass


class BaseModel(AbstractBaseModel):
    __abstract__ = True

    id: Any
    __name__: str

    def __str__(self) -> str:
        return f'<{type(self).__name__}: id={self.id}>'

    def __repr__(self) -> str:
        return f'<{type(self).__name__} object at 0x{id(self):x}: id={self.id}>'

    async def save(self, db: Session) -> None:
        await db.flush()
        await db.refresh(self)
