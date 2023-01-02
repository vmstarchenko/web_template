from typing import Optional
import datetime

from jose import jwt
from sqlalchemy import (
    Boolean, Column, Integer, DateTime, ForeignKey
)
from sqlmodel import Relationship, Field

from app.db import BaseModel, BaseCRUD, Session

from app.core import security, settings

from .user import User

from sqlmodel import select

class CRUD(BaseCRUD['Token']):
    def load(self, db: Session, payload: dict[str, str | datetime.datetime]) -> 'Token':
        # return db.exec(select(Token).where(Token.id == payload['tid'])).one()
        return self.get(db, id=payload['tid'])


class Token(BaseModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    is_active: bool = Field(default=True)
    last_usage: datetime.datetime = Field(
        sa_column=Column(
            DateTime(timezone=True),
            default=lambda: datetime.datetime.now()
        ),
    )  # pylint: disable=unnecessary-lambda
    user_id: int = Field(foreign_key='user.id')
    user: User = Relationship(back_populates='token')

    def encode(self, expires_delta: datetime.timedelta | None = None) -> str:
        if expires_delta is not None:
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

Token.crud = CRUD(Token)
