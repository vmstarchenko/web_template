from typing import AsyncIterable, Any
import functools

from httpx import AsyncClient as Client
import pytest
from sqlalchemy.orm import sessionmaker


from app import deps, models
from app.db import configure, Session, BaseModel, SessionMeta
from app.core import settings
from app.main import app

import sqlalchemy
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy.orm import sessionmaker, Session as OrmSession
from sqlalchemy.pool import StaticPool


@pytest.fixture()
async def db_initials() -> AsyncIterable[Any]:
    uri = 'sqlite+aiosqlite://'

    TestSession: SessionMeta = sessionmaker(  # type: ignore
        expire_on_commit=False,
        class_=Session,
    )

    conf = configure(uri=uri, Session=TestSession)
    engine = conf['engine']

    meta = BaseModel.metadata
    async with engine.begin() as conn:
        await conn.run_sync(meta.drop_all)
        await conn.run_sync(meta.create_all)

        yield {'Session': TestSession}

        await conn.run_sync(meta.drop_all)


@pytest.fixture()
async def db(db_initials: Any, client: Client) -> AsyncIterable[Session]:
    async for db in app.dependency_overrides[deps.get_db]():
        yield db


@pytest.fixture()
async def client(db_initials: Any) -> AsyncIterable[Client]:
    async with Client(app=app, base_url='http://test') as client:
        app.dependency_overrides[deps.get_db] = deps.DbDependency(Session=db_initials['Session'])
        yield client


@pytest.fixture()
async def user(client: Client, db: Session) -> AsyncIterable[models.User]:
    obj = await models.User.crud.create(db, email='test@test.example', password='password', username='user')
    # obj.headers = await get_user_headers(client, 'username', 'password')
    yield obj
    # obj.delete()  # TODO


@pytest.fixture()
async def superuser(client: Client, db: Session) -> AsyncIterable[models.User]:
    obj = await models.User.crud.create(
        db,
        email='superuser@test.example', password='password', username='superuser',
        is_superuser=True,
    )
    # obj.headers = await get_user_headers(client, 'superuser', 'password')
    yield obj
    # obj.delete()  # TODO


@pytest.fixture()
async def user_headers(client: Client, user: models.User) -> AsyncIterable[dict[str, str]]:
    yield await get_user_headers(client, 'user', 'password')


@pytest.fixture()
async def superuser_headers(client: Client, superuser: models.User) -> AsyncIterable[dict[str, str]]:
    yield await get_user_headers(client, 'superuser', 'password')



async def get_user_headers(client: Client, username: str, password: str) -> dict[str, str]:
    resp = await client.post(settings.TOKEN_URL, data={
        'username': username, 'password': password
    })
    res = resp.json()
    assert resp.status_code == 200, res
    token = res.get('access_token')
    assert token, res

    return {'Authorization': f'Bearer {token}'}

