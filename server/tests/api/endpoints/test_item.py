import pytest


def test_item_create(client) -> None:
    resp = client.post('/api/item/')
    res = resp.json()
    assert resp.status_code == 200, res
    assert res == {'id': 1}, res


def test_item_get(client) -> None:
    client.post('/api/item/')

    resp = client.get('/api/item/1/')
    assert resp.status_code == 200
    res = resp.json()
    assert res == {'id': 1}, res


def test_item_get_missing(client) -> None:
    resp = client.get('/api/item/404/')
    assert resp.status_code == 404
    res = resp.json()
    assert res == {'detail': 'Not Found'}, res
