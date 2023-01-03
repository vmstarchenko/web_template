from fastapi import Depends, HTTPException, status  # , Header
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, ExpiredSignatureError
from pydantic import ValidationError
from sqlalchemy.exc import NoResultFound

from app.db.deps import get_db, DbDependency
from app.db import Session
from app.core import settings
from app.models import User

from app.models.user import get_current_user

__all__ = ('get_db',)



def get_current_superuser(user: User = Depends(get_current_user)) -> User:
    if not user.is_superuser:
        raise HTTPException(
            status_code=400, detail="The user doesn't have enough privileges"
        )
    return user

