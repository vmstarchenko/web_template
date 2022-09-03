from typing import AsyncIterable
import functools

from httpx import AsyncClient as Client
import pytest
from sqlalchemy.orm import sessionmaker


from app import deps, db as db_, models
from app.core import settings
from app.main import app

import sqlalchemy
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy.orm import sessionmaker, Session as OrmSession
from sqlalchemy.pool import StaticPool


@pytest.fixture()
async def db_initials():
    uri = 'sqlite+aiosqlite://'

    TestSession = sessionmaker(
        expire_on_commit=False,
        class_=db_.Session,
    )

    conf = db_.configure(uri=uri, Session=TestSession)
    engine = conf['engine']

    meta = db_.Base.metadata
    async with engine.begin() as conn:
        await conn.run_sync(meta.drop_all)
        await conn.run_sync(meta.create_all)

        yield {'Session': TestSession}

        await conn.run_sync(meta.drop_all)


@pytest.fixture()
async def db(db_initials, client):
    async for db in app.dependency_overrides[deps.get_db]():
        yield db


@pytest.fixture()
async def client(db_initials) -> AsyncIterable[Client]:
    async with Client(app=app, base_url='http://test') as client:
        app.dependency_overrides[deps.get_db] = deps.DbDependency(Session=db_initials['Session'])
        yield client


@pytest.fixture()
async def user(client, db):
    obj = await models.User.Manager(models.User, db).create(email='test@test.example', password='password', username='username')
    obj.headers = await get_user_headers(client, 'username', 'password')
    yield obj
    # obj.delete()  # TODO


@pytest.fixture()
async def superuser(client, db):
    obj = await models.User.Manager(models.User, db).create(
        email='superuser@test.example', password='password', username='superuser',
        is_superuser=True,
    )
    obj.headers = await get_user_headers(client, 'superuser', 'password')
    yield obj
    # obj.delete()  # TODO


async def get_user_headers(client, username, password):
    resp = await client.post(settings.TOKEN_URL, data={
        'username': username, 'password': password
    })
    res = resp.json()
    assert resp.status_code == 200, res
    token = res.get('access_token')
    assert token, res

    return {'Authorization': f'Bearer {token}'}
