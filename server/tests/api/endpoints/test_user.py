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
        {'email': 'superuser@test.example', 'is_active': True, 'is_superuser': True, 'id': 1}
    ], res

# TODO: enable this test
# async def test_user_get_with_invalid_id(client: Client) -> None:
#     resp = await client.get('/api/user/abacaba/')
#     assert resp.status_code == 200, res
#     assert res == {}, res

async def test_user_register(client: Client, smtp_server) -> None:
    resp = await client.post('/api/user/register/', json={'password': 'pass', 'email': 'new@test.example', 'username': 'new'})
    assert resp.status_code == 200, res
    res = resp.json()
    assert res == {'email': 'new@test.example', 'id': 1, 'is_active': False, 'is_superuser': False}, res

    assert len(smtp_server.mails) == 1, smtp_server.mails
    mail = smtp_server.mails[0]
    assert len(mail.links) == 1, mail.links

    resp = await client.get(mail.links[0])
    res = resp.json()
    assert resp.status_code == 200, res
    assert res == {'email': 'new@test.example', 'id': 1, 'is_active': True, 'is_superuser': False}, res


