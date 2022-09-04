from typing import TypeVar, Generic, Any, cast
from sqlalchemy import select
from sqlalchemy.sql import Executable
from sqlalchemy.exc import NoResultFound
from fastapi.encoders import jsonable_encoder

from .session import Session

T = TypeVar('T', bound='BaseModel')
_DEFAULT = object()


class BaseCRUD(Generic[T]):
    def __init__(self, Model: type[T]):  # pylint: disable=invalid-name
        self.Model = Model  # pylint: disable=invalid-name

    async def create(self, db: Session, *, save_: bool = True, **kwargs: Any) -> T:
        obj = self.Model(**kwargs)
        db.add(obj)
        if save_:
            await obj.save(db)
        return obj

    def _get_query(self, *conditions: Any, **kv_conditions: Any) -> Executable:
        query = select(self.Model)
        if conditions:
            query = query.filter(*conditions)
        if kv_conditions:
            query = query.filter_by(**kv_conditions)
        return query

    async def get(self, db: Session, *conditions: Any, **kv_conditions: Any) -> T:
        return cast(  # TODO: remove cast
            T,
            (await db.execute(self._get_query(*conditions, **kv_conditions))).scalar_one(),
        )

    async def get_or_create(
            self, db: Session, *conditions: Any, save_: bool=True,
            defaults_: dict[str, Any] | None = None, **kv_conditions: Any,
            ) -> tuple[bool, T]:
        try:
            created, obj = False, await self.get(*conditions, save_=save_, **kv_conditions)
        except NoResultFound:
            created, obj = True, await self.create(**(defaults_ or {}), save_=save_)
        return created, obj

    async def update(
            self, db: Session, obj: T, obj_in: Any=None, save_: bool=True, **kwargs: Any
            ) -> T:
        # if isinstance(obj, dict):
        #     kwargs.update(obj_in)
        # else:
        kwargs.update(obj_in.dict(exclude_unset=True))

        obj_data = jsonable_encoder(obj)
        for field in obj_data:
            value = kwargs.get(field, _DEFAULT)
            if value is not _DEFAULT:
                setattr(obj, field, value)

        db.add(obj)
        if save_:
            await obj.save(db)
        return obj

    # def get_multi_by_user(self, *, user_id: int, skip: int = 0, limit: int = 100) -> list[T]:
    #     return await db.execute(
    #         select(self.Model)
    #         .filter(self.Model.user_id == user_id)
    #         .offset(skip)
    #         .limit(limit)
    #         .all()
    #     )

    # def get_multi(self, *, skip: int = 0, limit: int = 100) -> list[T]:
    #     return db.query(self.Model).offset(skip).limit(limit).all()

    # def get_all(self, *condition) -> list[T]:
    #     return db.query(self.Model).filter(*condition).all()

    # def search(self, *condition) -> list[T]:
    #     return db.query(self.Model).filter(*condition)


    # async def remove(self, db: Session, *conditions: Any, **kv_conditions: Any) -> None:
    #     await db.execute(self._get_query(*conditions, **kv_conditions).delete())


from .base_model import BaseModel, BaseModelMeta  # pylint: disable=unused-import,wrong-import-position,cyclic-import
