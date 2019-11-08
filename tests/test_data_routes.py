import asyncio
from starlette.testclient import TestClient
from app import app
from testing_utilities import get_auth_header

mclient = TestClient(app)


def test_pulse():
    response = mclient.get('/pulse')
    assert response.status_code == 200


def test_atm_ivol_without_params():
    with TestClient(app) as client:
        headers = get_auth_header('simple-active',client)
        response = client.get('/ivol/atm', headers=headers)
        assert response.status_code == 422


def test_atm_ivol_without_creds():
    with TestClient(app) as client:
        params = {'symbol': 'cl'}
        response = client.get('/ivol/atm', params=params)
        assert response.status_code == 401


def test_atm_ivol():
    with TestClient(app) as client:
        headers = get_auth_header('simple-active', client)
        params = {'symbol': 'cl'}
        response = client.get('/ivol/atm', params=params, headers=headers)
        assert response.status_code == 200


def test_ivol_surface():
    with TestClient(app) as client:
        headers = get_auth_header('simple-active', client)
        response = client.get('/ivol/surface', headers=headers)
        assert response.status_code == 422


def test_surface_wihtout_creds():
    with TestClient(app) as client:
        params = {'symbol': 'cl'}
        response = client.get('/ivol/surface', params=params)
        assert response.status_code == 401


def test_surface():
    with TestClient(app) as client:
        headers = get_auth_header('simple-active', client)
        params = {'symbol': 'cl'}
        response = client.get('/ivol/surface', params=params, headers=headers)
        assert response.status_code == 200


