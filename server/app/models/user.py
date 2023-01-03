from typing import AsyncGenerator, Any

from fastapi import Depends
from fastapi_users.db import SQLAlchemyBaseUserTable, SQLAlchemyUserDatabase
# from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
# from sqlalchemy.ext.declarative import DeclarativeMeta, declarative_base
# from sqlalchemy.orm import sessionmaker
from sqlalchemy import Column, Integer, String

from app.db import SABaseModel, Session
from app.core.security import get_password_hash, verify_password

# DATABASE_URL = "sqlite+aiosqlite:///./test.db"
# Base: DeclarativeMeta = declarative_base()

from app.db.crud import BaseCRUD

class User(SQLAlchemyBaseUserTable[int], SABaseModel):
    id: int = Column(Integer, primary_key=True, autoincrement=True)
    username: str = Column(String(length=32), nullable=False, unique=True, index=True)

# print(User.get_by_email)

# engine = create_async_engine(DATABASE_URL)
# async_session_maker = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)


# async def create_db_and_tables():
#     async with engine.begin() as conn:
#         await conn.run_sync(Base.metadata.create_all)


# async def get_async_session() -> AsyncGenerator[AsyncSession, None]:
#     async with async_session_maker() as session:
#         yield session

from app.db.deps import get_db

async def get_user_db(session = Depends(get_db)):
    db = SQLAlchemyUserDatabase(session, User)
    yield db

from typing import Optional

from fastapi import Depends, Request
from fastapi_users import BaseUserManager, FastAPIUsers, IntegerIDMixin
from fastapi_users.authentication import (
    AuthenticationBackend,
    BearerTransport,
    JWTStrategy,
)
from fastapi_users.db import SQLAlchemyUserDatabase

SECRET = "SECRET"

from app.utils import send_new_account_email

class UserManager(IntegerIDMixin, BaseUserManager[User, int]):
    reset_password_token_secret = SECRET
    verification_token_secret = SECRET

    async def on_after_register(self, user: User, request: Optional[Request] = None):
        if request is None:
            return

        url = request.url
        link = f'{url.scheme}://{url.hostname}/api/user/verify/{user.id}/'
        send_new_account_email(link=link, email=user.email, username=user.username)

    async def on_after_forgot_password(
        self, user: User, token: str, request: Optional[Request] = None
    ):
        print(f"User {user.id} has forgot their password. Reset token: {token}")

    async def on_after_request_verify(
        self, user: User, token: str, request: Optional[Request] = None
    ):
        print(f"Verification requested for user {user.id}. Verification token: {token}")


async def get_user_manager(user_db: SQLAlchemyUserDatabase = Depends(get_user_db)):
    m = UserManager(user_db)
    yield m

import contextlib
get_user_db_context = contextlib.asynccontextmanager(get_user_db)
get_user_manager_context = contextlib.asynccontextmanager(get_user_manager)

bearer_transport = BearerTransport(tokenUrl="auth/jwt/login")


def get_jwt_strategy() -> JWTStrategy:
    return JWTStrategy(secret=SECRET, lifetime_seconds=3600)


auth_backend = AuthenticationBackend(
    name="jwt",
    transport=bearer_transport,
    get_strategy=get_jwt_strategy,
)

fastapi_users = FastAPIUsers[User, int](get_user_manager, [auth_backend])

current_active_user = fastapi_users.current_user(active=True)

class CRUD(BaseCRUD['User']):
    async def create(self, db: Session, **kwargs: Any) -> 'User':
        from app.schemas.user import UserCreate
        # kwargs['hashed_password'] = get_password_hash(kwargs.pop('password'))

        async with get_user_db_context(db) as user_db:
            async with get_user_manager_context(user_db) as user_manager:
                user = await user_manager.create(UserCreate(**kwargs))
        print(user.email)
        return user

    '''
    async def authenticate(self, db: Session, *, username: str, password: str) -> 'User':
        user = await self.get(db, username=username)
        if not verify_password(password, str(user.hashed_password)):
            raise ValueError('Invalid password')
        return user

    '''


User.crud = CRUD(User)
