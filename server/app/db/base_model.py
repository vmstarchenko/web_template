from sqlalchemy.ext.declarative import declarative_base
from .session import Session

from sqlmodel import SQLModel


Base = declarative_base(metadata=SQLModel.metadata)
# SQLModel.metadata = AbstractBaseModel.metadata


class BaseModelMixin:
    __config__ = {}

    def __str__(self) -> str:
        return f'<{type(self).__name__}: id={self.id}>'

    def __repr__(self) -> str:
        return f'<{type(self).__name__} object at 0x{id(self):x}: id={self.id}>'

    async def save(self, db: Session) -> None:
        await db.flush()
        await db.refresh(self)


class SABaseModel(BaseModelMixin, Base):
    __abstract__ = True


class BaseModel(SQLModel, BaseModelMixin):
    pass
