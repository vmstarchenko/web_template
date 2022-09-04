import pytest
from httpx import AsyncClient


async def test_item_create(client: AsyncClient) -> None:
    resp = await client.post('/api/item/')
    res = resp.json()
    assert resp.status_code == 200, res
    assert res == {'id': 1}, res


async def test_item_get(client: AsyncClient) -> None:
    await client.post('/api/item/')

    resp = await client.get('/api/item/1/')
    assert resp.status_code == 200
    res = resp.json()
    assert res == {'id': 1}, res


async def test_item_get_missing(client: AsyncClient) -> None:
    resp = await client.get('/api/item/404/')
    assert resp.status_code == 404
    res = resp.json()
    assert res == {'detail': 'Not Found'}, res
