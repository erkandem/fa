from starlette.testclient import TestClient
from app import app


client = TestClient(app)


def test_pulse():
    response = client.get('/heartbeat')
    assert response.status_code == 200


def test_atm_ivol_without_params():
    with TestClient(app) as client:
        response = client.get('/ivol/atm')
    assert response.status_code == 422


def test_atm_ivol():
    params = {
        'symbol': 'cl',
    }
    with TestClient(app) as client:
        response = client.get(
            '/ivol/atm',
            params=params,
        )
    assert response.status_code == 200


def test_general_ivol():
    params = {
        'symbol': 'cl',
    }
    with TestClient(app) as client:
        response = client.get(
            '/ivol',
            params=params,
        )
    assert response.status_code == 200


def test_ivol_surface():
    with TestClient(app) as client:
        response = client.get('/ivol/surface')
    assert response.status_code == 422


def test_surface():
    params = {
        'symbol': 'cl',
    }
    with TestClient(app) as client:
        response = client.get(
            '/ivol/surface',
            params=params,
        )
    assert response.status_code == 200


def test_prices_intraday():
    params = {
        'symbol': 'cl',
        'month': 'g',
        'year': 19,
        'startdate': '2019-01-01',
    }
    with TestClient(app) as client:
        response = client.get(
            '/prices/intraday',
            params=params,
        )
    assert response.status_code == 200


def test_prices_intraday_pvp():
    params = {
        'symbol': 'cl',
        'month': 'g',
        'year': 19,
        'startdate': '2019-01-01',
    }
    with TestClient(app) as client:
        response = client.get(
            '/prices/intraday/pvp',
            params=params,
        )
    assert response.status_code == 200


def test_prices_eod_conti():
    params = {
        'symbol': 'cl',
    }
    with TestClient(app) as client:
        response = client.get(
            '/prices/eod/conti',
            params=params,
        )
    assert response.status_code == 200


def test_prices_eod_conti_array():
    params = {
        'symbol': 'cl',
    }
    with TestClient(app) as client:
        response = client.get(
            '/prices/eod/conti/array',
            params=params,
        )
    assert response.status_code == 200


def test_prices_eod():
    params = {
        'symbol': 'cl',
        'month': 'g',
        'year': 2019,
        'startdate': '2019-01-01',
    }
    with TestClient(app) as client:
        response = client.get(
            '/prices/eod',
            params=params,
        )
    assert response.status_code == 200


def test_ivol_smile():
    params = {
        'symbol': 'cl',
    }
    with TestClient(app) as client:
        response = client.get(
            '/ivol/smile',
            params=params,
        )
    assert response.status_code == 200


def test_risk_reversal():
    params = {
        'symbol': 'hyg',
    }
    with TestClient(app) as client:
        response = client.get(
            '/ivol/risk-reversal',
            params=params,
        )
    assert response.status_code == 200


def test_calendar_spread():
    params = {
        'symbol': 'spy',
    }
    with TestClient(app) as client:
        response = client.get(
            '/ivol/calendar',
            params=params,
        )
    assert response.status_code == 200


def test_summary_route():
    params = {
        'symbol': 'spy',
    }
    with TestClient(app) as client:
        response = client.get(
            '/ivol/summary/single',
            params=params,
        )
    assert response.status_code == 200


def test_summary_cme_route():
    with TestClient(app) as client:
        response = client.get('/ivol/summary/cme')
    assert response.status_code == 200


def test_summary_ice_route():
    with TestClient(app) as client:
        response = client.get('/ivol/summary/ice')
    assert response.status_code == 200


def test_summary_usetf_route():
    with TestClient(app) as client:
        response = client.get('/ivol/summary/usetf')
    assert response.status_code == 200


def test_summary_eurex_route():
    with TestClient(app) as client:
        response = client.get('/ivol/summary/eurex')
    assert response.status_code == 200


def test_inter_spread_route():
    params = {
        'symbol1': 'spy',
        'symbol2': 'ewz',
    }
    with TestClient(app) as client:
        response = client.get(
            '/ivol/inter-spread',
            params=params,
        )
    assert response.status_code == 200


def test_topoi_route():
    headers = {
        'Content-Type': 'application/json',
    }
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
        "order": "desc",
        }
    with TestClient(app) as client:
        response = client.post(
            '/top-oi-and-volume',
            json=body,
            headers=headers,
        )
    assert response.status_code == 200


def test_delta_contour_data():
    headers = {
        'Content-Type': 'application/json',
    }
    body = {
        "ust": "fut",
        "exchange": "cme",
        "symbol": "cl",
        "option_month": "201912",
        "underlying_month": "201912",
        "startdate": "2019-01-01",
        "enddate": "2019-04-01",
        "ltd": "20191115",
    }
    with TestClient(app) as client:
        response = client.post(
            '/delta-contour',
            json=body,
            headers=headers,
        )
    assert response.status_code == 200


def test_raw_option_data():
    headers = {
        'Content-Type': 'application/json',
    }
    body = {
        "ust": "eqt",
        "exchange": "usetf",
        "symbol": "spy",
        "putcall": "put",
        "ltd": "20200117",
        "metric": "rawiv",
        "strkpx": 250,
        "startdate": "2019-01-01",
        "enddate": "2019-04-01",
    }
    with TestClient(app) as client:
        response = client.post(
            '/option-data',
            json=body,
            headers=headers,
        )
    assert response.status_code == 200


def test_rawdata_all_options_csv():
    headers = {
        'Accept': 'application/csv',
    }
    params = {
        'symbol': 'ewz',
        'date': '2020-01-24',
    }
    with TestClient(app) as client:
        response = client.get(
            url='/option-data/single-underlying-single-day',
            headers=headers,
            params=params,
        )
    assert response.status_code == 200


def test_rawdata_all_options_json():
    headers = {
        'Accept': 'application/json',
    }
    params = {
        'symbol': 'ewz',
        'date': '2020-01-24',
    }
    with TestClient(app) as client:
        response = client.get(
            url='/option-data/single-underlying-single-day',
            params=params,
            headers=headers,
        )
    assert response.status_code == 200
