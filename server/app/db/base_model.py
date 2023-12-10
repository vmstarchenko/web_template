from typing import Any, ClassVar
from sqlalchemy.ext.declarative import declared_attr, DeclarativeMeta
from sqlmodel import SQLModel, MetaData
from sqlmodel.main import SQLModelMetaclass, default_registry

from .session import Session


naming_convention = {
    "ix": 'ix_%(column_0_label)s',
    "uq": "uq_%(table_name)s_%(column_0_name)s",
    "ck": "ck_%(table_name)s_%(column_0_name)s",
    "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
    "pk": "pk_%(table_name)s"
}

metadata = MetaData(naming_convention=naming_convention)
default_registry.metadata = metadata
Base: DeclarativeMeta = default_registry.generate_base()
SQLModel.metadata = Base.metadata


class BaseModelMetaclassMixin:
    def __new__(
            cls: Any,
            name: str, bases: tuple[type[Any], ...], attrs: dict[str, Any],
            **kwargs: Any
            ) -> 'BaseModelMetaclassMixin':

        annotations = attrs.setdefault('__annotations__', {})

        CRUD = annotations.get('crud')  # pylint: disable=invalid-name

        if CRUD is not None:
            annotations['crud'] = ClassVar[CRUD]

        obj = super().__new__(cls, name, bases, attrs, **kwargs)  # type: ignore

        if CRUD is not None:
            obj.crud = CRUD(obj)

        return obj  # type: ignore


class BaseModelMetaclass(BaseModelMetaclassMixin, SQLModelMetaclass):  # pylint: disable=too-many-ancestors
    pass


class SABaseModelMetaclass(BaseModelMetaclassMixin, DeclarativeMeta):
    pass


class AbstractBase:
    __config__ = {}  # type: ignore
    id: Any

    def __str__(self) -> str:
        return f'<{type(self).__name__}: id={self.id}>'

    def __repr__(self) -> str:
        return f'<{type(self).__name__} object at 0x{id(self):x}: id={self.id}>'

    async def save(self, db: Session) -> None:
        await db.flush()
        await db.refresh(self)


class SABaseModel(Base, AbstractBase, metaclass=SABaseModelMetaclass):  # type: ignore
    __abstract__ = True

    @declared_attr  # type: ignore
    def __tablename__(cls: DeclarativeMeta) -> str:    # pylint: disable=no-self-argument
        return cls.__name__.lower()    # pylint: disable=no-member


class BaseModel(SQLModel, AbstractBase, metaclass=BaseModelMetaclass):
    pass
    # class Config:
    #     arbitrary_types_allowed = True
