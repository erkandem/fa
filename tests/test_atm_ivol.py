from starlette.testclient import TestClient
from app import app
import asyncio


def test_basic():
    with TestClient(app) as client:
        response = client.get('/ivol/atm')
        assert response.status_code == 422


def test_specific():
    with TestClient(app) as client:
        params = {'symbol': 'cl'}
        response = client.get('/ivol/atm', params=params)
        assert response.status_code == 200

