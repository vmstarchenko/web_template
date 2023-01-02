from typing import TypeVar, Generic, Any, cast
from sqlalchemy import select
from sqlalchemy.sql import Executable
from sqlalchemy.exc import NoResultFound
from fastapi import HTTPException
from fastapi.encoders import jsonable_encoder

from .session import Session

T = TypeVar('T', bound='BaseModel')
_DEFAULT = object()


class BaseCRUD(Generic[T]):
    def __init__(self, model: type[T]):  # pylint: disable=invalid-name
        self.model = model  # pylint: disable=invalid-name

    def create(self, db: Session, *, save_: bool = True, **attrs: Any) -> T:
        obj = self.model(**attrs)
        db.add(obj)
        if save_:
            obj.save(db)
        return obj

    def get_query(self, **kv_conditions: Any) -> Executable:
        query = select(self.model)
        if kv_conditions:
            query = query.filter_by(**kv_conditions)
        return query

    def get(self, db: Session, **kv_conditions: Any) -> T:
        return cast(  # TODO: remove cast
            T,
            (db.execute(self.get_query(**kv_conditions))).scalar_one(),
        )

    def get_or_create(
            self, db: Session, save_: bool=True,
            defaults_: dict[str, Any] | None = None, **kv_conditions: Any,
            ) -> tuple[bool, T]:
        try:
            created, obj = False, self.get(save_=save_, **kv_conditions)
        except NoResultFound:
            created, obj = True, self.create(**(defaults_ or {}), save_=save_)
        return created, obj

    def get_or_404(self, db: Session, detail_: str | None = None, **kv_conditions: Any) -> T:
        try:
            return self.get(db, **kv_conditions)
        except NoResultFound as e:
            raise HTTPException(status_code=404, detail=detail_) from e

    def get_or_none(self, db: Session, **kv_conditions: Any) -> T | None:
        try:
            return self.get(db, **kv_conditions)
        except NoResultFound:
            return None

    def update(
            self, db: Session, obj: T, obj_in: Any=None, save_: bool=True, **kwargs: Any
            ) -> T:
        # if isinstance(obj, dict):
        #     kwargs.update(obj_in)
        # else:
        # kwargs.update(obj_in.dict(exclude_unset=True))

        obj_data = jsonable_encoder(obj)
        for field in obj_data:
            value = kwargs.get(field, _DEFAULT)
            if value is not _DEFAULT:
                setattr(obj, field, value)

        db.add(obj)
        if save_:
            obj.save(db)
        return obj

    # def get_multi_by_user(self, *, user_id: int, skip: int = 0, limit: int = 100) -> list[T]:
    #     return db.execute(
    #         select(self.model)
    #         .filter(self.model.user_id == user_id)
    #         .offset(skip)
    #         .limit(limit)
    #         .all()
    #     )

    # def get_multi(self, *, skip: int = 0, limit: int = 100) -> list[T]:
    #     return db.query(self.model).offset(skip).limit(limit).all()

    # def get_all(self, *condition) -> list[T]:
    #     return db.query(self.model).filter(*condition).all()

    # def search(self, *condition) -> list[T]:
    #     return db.query(self.model).filter(*condition)


    # def remove(self, db: Session, *conditions: Any, **kv_conditions: Any) -> None:
    #     db.execute(self.get_query(*conditions, **kv_conditions).delete())


from .base_model import BaseModel # pylint: disable=unused-import,wrong-import-position,cyclic-import
