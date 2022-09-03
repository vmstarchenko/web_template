from typing import TypeVar, Generic
from sqlalchemy import select
from sqlalchemy.exc import NoResultFound
from fastapi.encoders import jsonable_encoder

from .session import Session

T = TypeVar('T', bound='Base')
_DEFAULT = object()


class BaseManager(Generic[T]):
    def __init__(self, Model, db: Session):  # pylint: disable=invalid-name
        self.db = db
        self.Model = Model  # pylint: disable=invalid-name

    async def create(self, *, save_=True, **kwargs) -> T:
        obj = self.Model(**kwargs)
        self.db.add(obj)
        if save_:
            await obj.save(self.db)
        return obj

    def _get_query(self, *conditions, **kv_conditions):
        query = select(self.Model)
        if conditions:
            query = query.filter(*conditions)
        if kv_conditions:
            query = query.filter_by(**kv_conditions)
        return query

    async def get(self, *conditions, **kv_conditions) -> T:
        return (await self.db.execute(self._get_query(*conditions, **kv_conditions))).scalar_one()

    async def get_or_create(
            self, *conditions, save_=True, defaults_=None, **kv_conditions,
            ) -> tuple[bool, T]:
        try:
            created, obj = False, await self.get(*conditions, save_=save_, **kv_conditions)
        except NoResultFound:
            created, obj = True, await self.create(**(defaults_ or {}), save_=save_)
        return created, obj

    async def update(self, obj: T, obj_in=None, save_=True, **kwargs) -> T:
        if isinstance(obj, dict):
            kwargs.update(obj_in)
        else:
            kwargs.update(obj_in.dict(exclude_unset=True))

        obj_data = jsonable_encoder(obj)
        for field in obj_data:
            value = kwargs.get(field, _DEFAULT)
            if value is not _DEFAULT:
                setattr(obj, field, value)

        self.db.add(obj)
        if save_:
            await obj.save(self.db)
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
    #     return self.db.query(self.Model).offset(skip).limit(limit).all()

    # def get_all(self, *condition) -> list[T]:
    #     return self.db.query(self.Model).filter(*condition).all()

    # def search(self, *condition) -> list[T]:
    #     return self.db.query(self.Model).filter(*condition)


    async def remove(self, *conditions, **kv_conditions):
        await self.db.execute(self._get_query(*conditions, **kv_conditions).delete())


from .base_class import Base  # pylint: disable=unused-import,wrong-import-position,cyclic-import
