from typing import Any
from sqlalchemy.ext.declarative import DeclarativeMeta, declarative_base

from . import deps

from .session import Session
from .manager import BaseManager


class BaseModelMeta(DeclarativeMeta):
    def __new__(cls, name, bases, attrs):
        # if attrs.get('__annotations__'):
        #     attrs['__annotations__']['objects'] = attrs['Manager']

        if attrs.get('__tablename__', None) is None and not attrs.get('__abstract__', False):
            attrs['__tablename__'] = name.lower()
        return super().__new__(cls, name, bases, attrs)

    @property
    def objects(cls):
        return cls.Manager(cls, deps.get_db.from_context())

AbstractBaseModel = declarative_base(metaclass=BaseModelMeta)


class Base(AbstractBaseModel):
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

    class Manager(BaseManager['Base']):
        pass

    objects: Manager
