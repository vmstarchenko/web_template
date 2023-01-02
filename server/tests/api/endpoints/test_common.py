import pytest


def test_info(client) -> None:
    resp = client.get('/info/')
    assert resp.status_code == 200, resp
    res = resp.json()
    assert res == {
        'docs_url': 'http://testserver/docs',
        'info': 'Hello! This is api info page.',
        'redoc_url': 'http://testserver/redoc',
    }
