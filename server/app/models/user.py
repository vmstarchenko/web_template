from sqlalchemy import (
    Boolean, Column, Integer, String,
)

from app.db import Base, BaseManager
from app.core.security import get_password_hash, verify_password


class User(Base):
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    is_active = Column(Boolean(), default=True, nullable=False)
    is_superuser = Column(Boolean(), default=False, nullable=False)

    class Manager(BaseManager['User']):
        async def create(self, **kwargs) -> 'User':
            kwargs['hashed_password'] = get_password_hash(kwargs.pop('password'))
            return await super().create(**kwargs)

        async def authenticate(self, *, username: str, password: str) -> 'User':
            user = await self.get(username=username)
            if not verify_password(password, str(user.hashed_password)):
                raise ValueError('Invalid password')
            return user

    objects: Manager  # type: ignore
