from typing import AsyncIterable
import functools

from httpx import AsyncClient
import pytest
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import sessionmaker


from app import deps, db
from app.main import app

import sqlalchemy
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker, Session as OrmSession
from sqlalchemy.pool import StaticPool


@pytest.fixture()
async def db_initials():
    uri = 'sqlite+aiosqlite://'

    TestSession = sessionmaker(
        expire_on_commit=False,
        class_=AsyncSession,
    )

    conf = db.configure(uri=uri, Session=TestSession)
    engine = conf['engine']

    meta = db.Base.metadata
    async with engine.begin() as conn:
        await conn.run_sync(meta.drop_all)
        await conn.run_sync(meta.create_all)

        yield {'Session': TestSession}

        await conn.run_sync(meta.drop_all)


@pytest.fixture()
async def client(db_initials) -> AsyncIterable[AsyncClient]:
    async with AsyncClient(app=app, base_url='http://test') as client:
        app.dependency_overrides[deps.get_db] = deps.DbDependency(Session=db_initials['Session'])
        yield client
