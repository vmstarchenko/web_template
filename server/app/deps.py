from fastapi import Depends, HTTPException, status  # , Header
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, ExpiredSignatureError
from pydantic import ValidationError
from sqlalchemy.exc import NoResultFound

from app.db.deps import get_db, DbDependency
from app.db import Session
from app.core import settings
from app.models import User

__all__ = ('get_db', 'DbDependency')


reusable_oauth2 = OAuth2PasswordBearer(tokenUrl=settings.TOKEN_URL)


'''
def get_current_token(
    db: Session = Depends(get_db), jwt_token: str = Depends(reusable_oauth2),
    # user_agent: str | None = Header(None),
) -> Token:
    try:
        payload = Token.decode(jwt_token)
        token = Token.crud.load(db, payload)
    except ExpiredSignatureError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail='Token expired',
        ) from e
    except (JWTError, ValidationError, NoResultFound, ValueError) as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail='Could not validate credentials',
        ) from e

    return token


def get_current_user(token: Token = Depends(get_current_token)) -> User:
    return token.user



def get_current_superuser(user: User = Depends(get_current_user)) -> User:
    if not user.is_superuser:
        raise HTTPException(
            status_code=400, detail="The user doesn't have enough privileges"
        )
    return user
'''

from app.models.user import current_active_user as get_current_user
from app.models.user import current_active_user as get_current_token
