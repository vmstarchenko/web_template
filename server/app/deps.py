from fastapi import Depends, HTTPException, status  # , Header
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, ExpiredSignatureError
from pydantic import ValidationError
from sqlalchemy.orm import Session
from sqlalchemy.exc import NoResultFound

from app.db.deps import get_db, DbDependency
from app.core import settings
from app.models.token import Token, User

__all__ = ('get_db', 'DbDependency')


reusable_oauth2 = OAuth2PasswordBearer(tokenUrl=settings.TOKEN_URL)



async def get_current_token(
    db: Session = Depends(get_db), jwt_token: str = Depends(reusable_oauth2),
    # user_agent: str | None = Header(None),
) -> Token:
    try:
        payload = Token.decode(jwt_token)
        token = await Token.crud.load(db, payload)
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


async def get_current_user(token: Token = Depends(get_current_token)) -> User:
    return token.user


async def get_current_superuser(user: User = Depends(get_current_user)) -> User:
    if not user.is_superuser:
        raise HTTPException(
            status_code=400, detail="The user doesn't have enough privileges"
        )
    return user
