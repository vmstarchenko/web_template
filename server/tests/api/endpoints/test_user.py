from typing import Dict

from httpx import AsyncClient as Client
from app.models import User, Token
from app.core import settings


async def test_get_access_token(client: Client, user: User) -> None:
    login_data = {
        "username": "user",
        "password": "password"
    }
    resp = await client.post(settings.TOKEN_URL, data=login_data)
    assert resp.status_code == 200
    res = resp.json()
    assert "access_token" in res, res
    assert res["access_token"], res


async def test_use_token(client: Client, user_headers: dict[str, str]) -> None:
    resp = await client.get('/api/user/me/', headers=user_headers)
    assert resp.status_code == 200
    res = resp.json()
    assert "email" in res, res


async def test_use_invalid_token(client: Client, user_headers: dict[str, str]) -> None:
    resp = await client.get('/api/user/me/', headers={
        'Authorization': user_headers['Authorization'] + '_invalid',
    })
    assert resp.status_code == 401
    res = resp.json()
    assert res == {'detail': 'Could not validate credentials'}, res

    strange_token = Token(id=100, user_id=100).encode()
    resp = await client.get('/api/user/me/', headers={
        'Authorization': f'Bearer {strange_token}'
    })
    assert resp.status_code == 401
    res = resp.json()
    assert res == {'detail': 'Could not validate credentials'}, res


async def test_missing_token(client: Client, user: User) -> None:
    resp = await client.get('/api/user/me/')
    assert resp.status_code == 401
    res = resp.json()
    assert res == {'detail': 'Not authenticated'}, res

async def test_user_list(client: Client, superuser_headers: dict[str, str]) -> None:
    resp = await client.get('/api/user/', headers=superuser_headers)
    assert resp.status_code == 200
    res = resp.json()
    assert res == [
        {'email': 'superuser@test.example', 'is_active': True, 'is_superuser': True, 'full_name': None, 'id': 1}
    ], res
