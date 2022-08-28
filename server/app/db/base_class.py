from typing import Any
from sqlalchemy.ext.declarative import as_declarative, declared_attr

from .session import Session


@as_declarative()
class Base:
    id: Any
    __name__: str

    @classmethod
    @declared_attr
    def __tablename__(cls) -> str:
        return cls.__name__.lower()

    async def save(self, db: Session) -> None:
        await db.flush()
        await db.refresh(self)
