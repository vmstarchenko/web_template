from typing import Any, Optional

from sqlalchemy import (
    Boolean, Column, Integer, String,
)
from sqlmodel import Field, Relationship

from app.db import BaseModel, BaseCRUD, Session
from app.core.security import get_password_hash, verify_password


class CRUD(BaseCRUD['User']):
    def create(self, db: Session, **kwargs: Any) -> 'User':
        kwargs['hashed_password'] = get_password_hash(kwargs.pop('password'))
        return super().create(db, **kwargs)

    def authenticate(self, db: Session, *, username: str, password: str) -> 'User':
        user = self.get(db, username=username)
        if not verify_password(password, str(user.hashed_password)):
            raise ValueError('Invalid password')
        return user


class User(BaseModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    username: str = Field(index=True, sa_column_kwargs={"unique": True})
    hashed_password: str
    email: str = Field(index=True, sa_column_kwargs={"unique": True})
    is_active: bool = Field(default=False)
    is_superuser: bool = Field(default=False)

    token: 'Token' = Relationship(back_populates='user')


User.crud = CRUD(User)

from .token import Token
