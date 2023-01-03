import pytest

from typing import AsyncIterable, Any

from app.db import configure, Session, BaseModel, SessionMeta, create_async_engine
from app import models
from app.core import settings

from .client import Client


@pytest.fixture(name='user')
async def user_fixture(client: Client, db: Session) -> AsyncIterable[models.User]:
    obj = await models.User.crud.create(
        db,
        email='user@test.example',
        password='password', username='user',
        is_active=True, is_verified=True,
    )
    # obj.headers = get_user_headers(client, 'username', 'password')
    yield obj
    # obj.delete()  # TODO


@pytest.fixture(name='superuser')
async def superuser_fixture(client: Client, db: Session) -> AsyncIterable[models.User]:
    obj = await models.User.crud.create(
        db,
        email='superuser@test.example', password='password', username='superuser',
        is_superuser=True,
        is_active=True
    )
    yield obj
    # obj.delete()  # TODO


@pytest.fixture()
def user_headers(client: Client, user: models.User) -> AsyncIterable[dict[str, str]]:
    yield get_user_headers(client, 'user@test.example', 'password')


@pytest.fixture()
def superuser_headers(client: Client, superuser: models.User) -> AsyncIterable[dict[str, str]]:
    yield get_user_headers(client, 'superuser@test.example', 'password')


def get_user_headers(client: Client, username: str, password: str) -> dict[str, str]:
    resp = client.post(settings.TOKEN_URL, data={
        'username': username, 'password': password
    })
    res = resp.json()
    assert resp.status_code == 200, res
    token = res.get('access_token')
    assert token, res

    return {'Authorization': f'Bearer {token}'}
