import pytest


async def test_info(client):
    resp = await client.get('/info/')
    assert resp.status_code == 200, resp
    res = resp.json()
    assert res == {
        'docs_url': 'http://test/docs',
        'info': 'Hello! This is api info page.',
        'redoc_url': 'http://test/redoc',
    }
