from starlette.testclient import TestClient
from app import app


client = TestClient(app)


def test_pulse():
    response = client.get('/heartbeat')
    assert response.status_code == 200


def test_get_atm_ivol():
    params = {
        'symbol': 'cl',
    }
    with TestClient(app) as client:
        url = app.url_path_for('get_atm_ivol')
        response = client.get(
            url=url,
            params=params,
        )
    assert response.status_code == 200


def test_get_ivol():
    params = {
        'symbol': 'cl',
    }
    with TestClient(app) as client:
        url = app.url_path_for('get_ivol')
        response = client.get(
            url=url,
            params=params,
        )
    assert response.status_code == 200


def test_get_surface_by_delta():
    params = {
        'symbol': 'cl',
    }
    with TestClient(app) as client:
        url = app.url_path_for('get_surface_by_delta')
        response = client.get(
            url=url,
            params=params,
        )
    assert response.status_code == 200


def test_get_intraday_prices():
    params = {
        'symbol': 'cl',
        'month': 'g',
        'year': 19,
        'startdate': '2019-01-01',
    }
    with TestClient(app) as client:
        url = app.url_path_for('get_intraday_prices')
        response = client.get(
            url= url,
            params=params,
        )
    assert response.status_code == 200


def test_get_pvp_intraday():
    params = {
        'symbol': 'cl',
        'month': 'g',
        'year': 19,
        'startdate': '2019-01-01',
    }
    with TestClient(app) as client:
        url = app.url_path_for('get_pvp_intraday')
        response = client.get(
            url=url,
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


def test_get_regular_futures_eod():
    params = {
        'symbol': 'cl',
        'month': 'g',
        'year': 2019,
        'startdate': '2019-01-01',
    }
    with TestClient(app) as client:
        url = app.url_path_for('get_regular_futures_eod')
        response = client.get(
            url=url,
            params=params,
        )
    assert response.status_code == 200


def test_get_ivol_smile():
    params = {
        'symbol': 'cl',
    }
    with TestClient(app) as client:
        url = app.url_path_for('get_ivol_smile')
        response = client.get(
            url=url,
            params=params,
        )
    assert response.status_code == 200


def test_get_risk_reversal():
    params = {
        'symbol': 'hyg',
    }
    with TestClient(app) as client:
        url = app.url_path_for('get_risk_reversal')
        response = client.get(
            url=url,
            params=params,
        )
    assert response.status_code == 200


def test_get_ivol_calendar():
    params = {
        'symbol': 'spy',
    }
    with TestClient(app) as client:
        url = app.url_path_for('get_ivol_calendar')
        response = client.get(
            url=url,
            params=params,
        )
    assert response.status_code == 200


def test_get_ivol_summary_single():
    params = {
        'symbol': 'spy',
    }
    with TestClient(app) as client:
        url = app.url_path_for('get_ivol_summary_single')
        response = client.get(
            url=url,
            params=params,
        )
    assert response.status_code == 200


def test_get_ivol_summary_cme():
    with TestClient(app) as client:
        url = app.url_path_for('get_ivol_summary_cme')
        response = client.get(
            url=url,
        )
    assert response.status_code == 200


def test_get_ivol_summary_ice():
    with TestClient(app) as client:
        url = app.url_path_for('get_ivol_summary_ice')
        response = client.get(
            url=url,
        )
    assert response.status_code == 200


def test_get_ivol_summary_usetf():
    with TestClient(app) as client:
        url = app.url_path_for('get_ivol_summary_usetf')
        response = client.get(
            url=url,
        )
    assert response.status_code == 200


def test_get_ivol_summary_eurex():
    with TestClient(app) as client:
        url = app.url_path_for('get_ivol_summary_eurex')
        response = client.get(
            url=url,
        )
    assert response.status_code == 200


def test_get_ivol_inter_spread():
    params = {
        'symbol1': 'spy',
        'symbol2': 'ewz',
    }
    with TestClient(app) as client:
        url = app.url_path_for('get_ivol_inter_spread')
        response = client.get(
            url=url,
            params=params,
        )
    assert response.status_code == 200


def test_post_top_oi_and_volume():
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
        url = app.url_path_for('post_top_oi_and_volume')
        response = client.post(
            url=url,
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
        url = app.url_path_for('post_delta_data')
        response = client.post(
            url=url,
            json=body,
            headers=headers,
        )
    assert response.status_code == 200


def test_post_raw_option_data():
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
        url = app.url_path_for('post_raw_option_data')
        response = client.post(
            url=url,
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


class test_get_all_options_single_underlying_single_day:
    def test_json(self):
        headers = {
            'Accept': 'application/json',
        }
        params = {
            'symbol': 'ewz',
            'date': '2020-01-24',
        }
        with TestClient(app) as client:
            url = app.url_path_for('get_all_options_single_underlying_single_day')
            response = client.get(
                url=url,
                params=params,
                headers=headers,
            )
        assert response.headers.get('content-type') == headers['Accept']
        assert response.status_code == 200

    def test_csv(self):
        headers = {
            'Accept': 'application/csv',
        }
        params = {
            'symbol': 'ewz',
            'date': '2020-01-24',
        }
        with TestClient(app) as client:
            url = app.url_path_for('get_all_options_single_underlying_single_day')
            response = client.get(
                url=url,
                params=params,
                headers=headers,
            )
        assert response.headers.get('content-type') == headers['Accept']
        assert response.status_code == 200


def test_get_continuous_eod_spread():
    headers = {
        'Accept': 'application/json',
    }
    params = {
        'symbol': 'cl',
    }
    with TestClient(app) as client:
        url = app.url_path_for('get_continuous_eod_spread')
        response = client.get(
            url=url,
            params=params,
            headers=headers,
        )
    assert response.status_code == 200


def test_get_api_info_usts():
    headers = {
        'Accept': 'application/json',
    }
    with TestClient(app) as client:
        url = app.url_path_for('get_api_info_usts')
        response = client.get(
            url=url,
            headers=headers,
        )
    assert response.status_code == 200


def test_get_api_info_exchanges():
    headers = {
        'Accept': 'application/json',
    }
    params = {
        "ust": "fut",
    }
    with TestClient(app) as client:
        url = app.url_path_for('get_api_info_exchanges')
        response = client.get(
            url=url,
            params=params,
            headers=headers,
        )
    assert response.status_code == 200


def test_get_api_info_symbols():
    headers = {
        'Accept': 'application/json',
    }
    params = {
        "ust": "fut",
        "exchange": "cme",
    }
    with TestClient(app) as client:
        url = app.url_path_for('get_api_info_symbols')
        response = client.get(
            url=url,
            params=params,
            headers=headers,
        )
    assert response.status_code == 200


def test_get_api_info_ltd():
    headers = {
        'Accept': 'application/json',
    }
    params = {
        "ust": "fut",
        "exchange": "cme",
        "symbol": "cl",
    }
    with TestClient(app) as client:
        url = app.url_path_for('get_api_info_ltd')
        response = client.get(
            url=url,
            params=params,
            headers=headers,
        )
    assert response.status_code == 200


def test_get_api_info_option_month_and_underlying_month():
    """
    TODO: why do we get 2 results here?
          Distinct? data corruption?
    """
    headers = {
        'Accept': 'application/json',
    }
    params = {
        "ust": "fut",
        "exchange": "cme",
        "symbol": "cl",
        "ltd": "20201117",
    }
    with TestClient(app) as client:
        url = app.url_path_for('get_api_info_option_month_and_underlying_month')
        response = client.get(
            url=url,
            params=params,
            headers=headers,
        )
    assert response.status_code == 200


def test_get_api_info_first_and_last():
    headers = {
        'Accept': 'application/json',
    }
    params = {
        "ust": "eqt",
        "exchange": "usetf",
        "symbol": "xop",
        "ltd": "20200117",
    }
    with TestClient(app) as client:
        url = app.url_path_for('get_api_info_first_and_last')
        response = client.get(
            url=url,
            params=params,
            headers=headers,
        )
    assert response.status_code == 200


def test_get_api_info_strikes():
    headers = {
        'Accept': 'application/json',
    }
    params = {
        "ust": "eqt",
        "exchange": "usetf",
        "symbol": "xop",
        "putcall": "call",
        "ltd": "20200117",
    }
    with TestClient(app) as client:
        url = app.url_path_for('get_api_info_strikes')
        response = client.get(
            url=url,
            params=params,
            headers=headers,
        )
    assert response.status_code == 200


def test_post_api_info_strikes():
    headers = {
        'Accept': 'application/json',
    }
    body = {
        "ust": "eqt",
        "exchange": "usetf",
        "symbol": "xop",
        "putcall": "call",
        "ltd": "20200117",
    }
    with TestClient(app) as client:
        url = app.url_path_for('post_api_info_strikes')
        response = client.post(
            url=url,
            json=body,
            headers=headers,
        )
    assert response.status_code == 200

