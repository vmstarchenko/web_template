import pytest
from httpx import AsyncClient


async def test_item(client: AsyncClient) -> None:
    resp = await client.get('/api/item/')
    assert resp.status_code == 200, resp
    res = resp.json()
    assert res == {'id': 1}
