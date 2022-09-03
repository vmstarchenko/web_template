import datetime

from jose import jwt
from sqlalchemy import (
    Boolean, Column, Integer, DateTime, ForeignKey
)
from sqlalchemy.orm import relationship

from app.db import Base, BaseManager

from app.core import security, settings

from .user import User

class Token(Base):
    id = Column(Integer, primary_key=True, index=True)
    is_active = Column(Boolean(), default=True, nullable=False)
    last_usage = Column(DateTime, nullable=False, default=lambda: datetime.datetime.now())  # pylint: disable=unnecessary-lambda
    user_id = Column(Integer, ForeignKey('user.id'), nullable=False)
    user: User = relationship(User, uselist=False, lazy='selectin')

    def encode(self, expires_delta: datetime.timedelta = None) -> str:
        if expires_delta:
            expire = datetime.datetime.utcnow() + expires_delta
        else:
            expire = datetime.datetime.utcnow() + datetime.timedelta(
                minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
            )
        to_encode = {
            'exp': expire,
            'uid': str(self.user_id),
            'tid': str(self.id),
        }
        jwt_token = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=security.ALGORITHM)
        return jwt_token

    @staticmethod
    def decode(jwt_token: str) -> dict[str, str | datetime.datetime]:
        payload = jwt.decode(
            jwt_token, settings.SECRET_KEY, algorithms=[security.ALGORITHM]
        )
        payload['uid'] = int(payload['uid'])
        payload['tid'] = int(payload['tid'])
        return payload


    class Manager(BaseManager['Token']):
        async def load(self, payload: dict[str, str | datetime.datetime]) -> 'Token':
            return await self.get(id=payload['tid'])

    objects: Manager  # type: ignore
