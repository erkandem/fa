import asyncio
from starlette.testclient import TestClient
from app import app
from testing_utilities import get_auth_header

mclient = TestClient(app)


def test_pulse():
    response = mclient.get('/heartbeat')
    assert response.status_code == 200


def test_atm_ivol_without_params():
    with TestClient(app) as client:
        headers = get_auth_header('simple-active', client)
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


def test_general_ivol():
    with TestClient(app) as client:
        headers = get_auth_header('simple-active', client)
        params = {'symbol': 'cl'}
        response = client.get('/ivol', params=params, headers=headers)
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


def test_prices_intraday():
    with TestClient(app) as client:
        headers = get_auth_header('simple-active', client)
        params = {'symbol': 'cl', 'month': 'g', 'year': 19, 'startdate': '2019-01-01'}
        response = client.get('/prices/intraday', params=params, headers=headers)
        assert response.status_code == 200


def test_prices_intraday_pvp():
    with TestClient(app) as client:
        headers = get_auth_header('simple-active', client)
        params = {'symbol': 'cl', 'month': 'g', 'year': 19, 'startdate': '2019-01-01'}
        response = client.get('/prices/intraday/pvp', params=params, headers=headers)
        assert response.status_code == 200


def test_prices_eod_conti():
    with TestClient(app) as client:
        headers = get_auth_header('simple-active', client)
        params = {'symbol': 'cl'}
        response = client.get('/prices/eod/conti', params=params, headers=headers)
        assert response.status_code == 200


def test_prices_eod_conti_array():
    with TestClient(app) as client:
        headers = get_auth_header('simple-active', client)
        params = {'symbol': 'cl'}
        response = client.get('/prices/eod/conti/array', params=params, headers=headers)
        assert response.status_code == 200


def test_prices_eod():
    with TestClient(app) as client:
        headers = get_auth_header('simple-active', client)
        params = {'symbol': 'cl', 'month': 'g', 'year': 2019, 'startdate': '2019-01-01'}
        response = client.get('/prices/eod', params=params, headers=headers)
        assert response.status_code == 200


def test_ivol_smile():
    with TestClient(app) as client:
        headers = get_auth_header('simple-active', client)
        params = {'symbol': 'cl'}
        response = client.get('/ivol/smile', params=params, headers=headers)
        assert response.status_code == 200


def test_risk_reversal():
    with TestClient(app) as client:
        headers = get_auth_header('simple-active', client)
        params = {'symbol': 'hyg'}
        response = client.get('/ivol/risk-reversal', params=params, headers=headers)
        assert response.status_code == 200


def test_calendar_spread():
    with TestClient(app) as client:
        headers = get_auth_header('simple-active', client)
        params = {'symbol': 'spy'}
        response = client.get('/ivol/calendar', params=params, headers=headers)
        assert response.status_code == 200


def test_summary_route():
    with TestClient(app) as client:
        headers = get_auth_header('simple-active', client)
        params = {'symbol': 'spy'}
        response = client.get('/ivol/summary/single', params=params, headers=headers)
        assert response.status_code == 200


def test_summary_cme_route():
    with TestClient(app) as client:
        headers = get_auth_header('simple-active', client)
        response = client.get('/ivol/summary/cme', headers=headers)
        assert response.status_code == 200


def test_summary_ice_route():
    with TestClient(app) as client:
        headers = get_auth_header('simple-active', client)
        response = client.get('/ivol/summary/ice', headers=headers)
        assert response.status_code == 200


def test_summary_usetf_route():
    with TestClient(app) as client:
        headers = get_auth_header('simple-active', client)
        response = client.get('/ivol/summary/usetf', headers=headers)
        assert response.status_code == 200


def test_summary_eurex_route():
    with TestClient(app) as client:
        headers = get_auth_header('simple-active', client)
        response = client.get('/ivol/summary/eurex', headers=headers)
        assert response.status_code == 200


def test_inter_spread_route():
    with TestClient(app) as client:
        headers = get_auth_header('simple-active', client)
        params = {'symbol1': 'spy', 'symbol2': 'ewz'}
        response = client.get('/ivol/inter-spread', params=params, headers=headers)
        assert response.status_code == 200


def test_topoi_route():
    with TestClient(app) as client:
        headers = get_auth_header('simple-active', client)
        headers['Content-Type'] = 'application/json'
        body = {
            "ust": "eqt",
            "exchange": "usetf",
            "symbol": "spy",
            "startdate": "2019-01-01",
            "enddate": "2019-04-01",
            "putcall": "call",
            "ltd": "20200117",
            "metric": "oi",
            "dminus": 60,
            "top_n": 5,
            "order": "desc"
            }
        response = client.post('/top-oi-and-volume', json=body, headers=headers)
        assert response.status_code == 200


def test_delta_contour_data():
    with TestClient(app) as client:
        headers = get_auth_header('simple-active', client)
        headers['Content-Type'] = 'application/json'
        body = {
            "ust": "fut",
            "exchange": "cme",
            "symbol": "cl",
            "option_month": "201912",
            "underlying_month": "201912",
            "startdate": "2019-01-01",
            "enddate": "2019-04-01",
            "ltd": "20191115"
        }
        response = client.post('/delta-contour', json=body, headers=headers)
        assert response.status_code == 200
