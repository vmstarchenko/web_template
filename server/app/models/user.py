from typing import Any

from sqlalchemy import (
    Boolean, Column, Integer, String,
)

from app.db import BaseModel, BaseCRUD, Session
from app.core.security import get_password_hash, verify_password

class CRUD(BaseCRUD['User']):
    async def create(self, db: Session, **kwargs: Any) -> 'User':
        kwargs['hashed_password'] = get_password_hash(kwargs.pop('password'))
        return await super().create(db, **kwargs)

    async def authenticate(self, db: Session, *, username: str, password: str) -> 'User':
        user = await self.get(db, username=username)
        if not verify_password(password, str(user.hashed_password)):
            raise ValueError('Invalid password')
        return user


class User(BaseModel):
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    is_active = Column(Boolean(), default=False, nullable=False)
    is_superuser = Column(Boolean(), default=False, nullable=False)

    crud: CRUD
