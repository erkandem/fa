"""
http://0.0.0.0:5000/prices/intraday?symbol=ewz
http://0.0.0.0:5000/prices/eod/conti?symbol=cl
http://0.0.0.0:5000/prices/eod/conti/array?symbol=cl


http://0.0.0.0:5000/prices/intraday?symbol=ewz&startdate=20191001
http://0.0.0.0:5000/prices/intraday?symbol=ewz&startdate=20191001&interval=1&iunit=day
 - custom response statuses: https://fastapi.tiangolo.com/tutorial/response-change-status-code/
 - JSONResponse is default
 - can be overwritten with
"""
from datetime import datetime as dt
from datetime import date
from typing import List
import asyncpg
import fastapi
from pydantic import BaseModel
from falib.db import engines, pgc
from src.conti_prices import conti_resolver
from src.conti_prices import conti_array_resolver
from src.conti_prices import ContiEodArray
from src.conti_prices import FuturesEodConti
from src.intraday_prices import prices_intraday_content
from src.intraday_prices import PricesIntraday
from starlette.status import *
from src.auth import auth_model_input, refresh_model_input, create_jwt_token
from src.auth import validate_user
from starlette.middleware.cors import CORSMiddleware
from src.pvp import resolve_pvp
from src.regular_futures import resolve_eod_futures
from src.atm import resolve_atm_ivol

app = fastapi.FastAPI(
    title='iVolAPI',
    version='2.0.1',
    description='implied volatility and price data for selected ETFs and futures',
)

origins = [
    "http://localhost",
    "http://localhost:8080",
]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event('startup')
async def startup():
    engines['prices'] = await asyncpg.create_pool(pgc.get_uri('prices_intraday'))
    engines['dev'] = await asyncpg.create_pool(pgc.get_uri('pymarkets_null'))
    engines['t2'] = await asyncpg.create_pool(pgc.get_uri('pymarkets_tests_db_two'))


@app.on_event('shutdown')
async def shutdown():
    await engines['prices'].close()
    await engines['dev'].close()
    await engines['t2'].close()


class Pulse(BaseModel):
    date: dt


@app.post('/login')
async def login_route(login: auth_model_input):
    """
    https://fastapi.tiangolo.com/tutorial/security/oauth2-jwt/
    https://frankie567.github.io/fastapi-users/usage/routes/
    https://frankie567.github.io/fastapi-users/configuration/full_example/
    :param login:
    :return:
    """
    if validate_user(login):
        token = await create_jwt_token(login)
        return {'access_token': f'{token}'}
    else:
        return {'error': 'login failed'}


@app.post('/refresh')
async def refresh_route(token: refresh_model_input):
    return {'refreshed_token': f'fresh_{token.token}'}


@app.get('/', response_model=Pulse, status_code=HTTP_200_OK)
async def root():
    return {'date': dt.now()}


@app.get('/pulse', response_model=Pulse)
async def pulse():
    return {'date': dt.now()}


@app.get('/prices/intraday', status_code=HTTP_200_OK)
async def conti_eod_prices(
        symbol: str, month: int = None, year: int = None, ust: str = None, exchange: str = None,
        startdate: str = None, enddate: str = None, dminus: int = 20,
        interval: int = 1, iunit: str = 'minutes',  order: str = 'asc'):
    args = {
        'symbol': symbol, 'month': month, 'year': year, 'ust': ust, 'exchange': exchange,
        'startdate': startdate, 'enddate': enddate, 'dminus': dminus,
        'interval': interval, 'iunit': iunit, 'order': order
    }
    content = await prices_intraday_content(args)
    return content


@app.get('/prices/intraday/pvp')
async def pvp(
        symbol: str, month: int = None, year: int = None, ust: str = None, exchange: str = None,
        startdate: str = None, enddate: str = None, dminus: int = 20,
        buckets: int = 100, iunit: str = 'minutes',  order: str = 'asc'):
    """
    price volume profile. histogram of intraday price data

    - **symbol**: example: 'SPY' or 'spy' (case insensitive)
    - **month**: only for futures - one of ['F', 'G', 'H', 'J', 'K', 'M', 'N', 'Q', 'U', 'V', 'X', 'Z']
    - **year**: only for futures - example: 2019
    - **ust**: underlying security type: ['fut', 'eqt', 'ind', 'fx']
    - **exchange**: one of: ['usetf', 'cme', 'ice', 'eurex']
    - **startdate**: format: yyyymmdd
    - **enddate**: format: yyyymmdd
    - **dminus**: indicate the number of days back from `enddate`
    - **buckets**: number of intervals in the histogram
    - **iunit**: one of ['minutes', 'hour, 'day', 'week', 'month']
    - **order**: one of ['asc', 'desc']
    """
    args = {
        'symbol': symbol, 'month': month, 'year': year, 'ust': ust, 'exchange': exchange,
        'startdate': startdate, 'enddate': enddate, 'dminus': dminus,
        'buckets': buckets, 'iunit': iunit, 'order': order
    }
    content = await resolve_pvp(args)
    return content


@app.get('/prices/eod')
async def get_regular_futures_eod(
        symbol: str, month: int = None, year: int = None, ust: str = None, exchange: str = None,
        startdate: str = None, enddate: str = None, dminus: int = 30, order: str = 'asc'):
    """prices """
    args = {
        'symbol': symbol, 'month': month, 'year': year, 'ust': ust, 'exchange': exchange,
        'startdate': startdate, 'enddate': enddate, 'dminus': dminus, 'order': order
    }
    content = await resolve_eod_futures(args)
    return content


@app.get('/ivol/atm')
async def atm_ivol(
        symbol: str, ust: str = None, exchange: str = None, tte: str = '1m',
        startdate: str = None, enddate: str = None, dminus: int = 30, order: str = 'asc'):
    """prices """
    args = {
        'symbol': symbol, 'ust': ust, 'exchange': exchange, 'tte': tte,
        'startdate': startdate, 'enddate': enddate, 'dminus': dminus, 'order': order
    }
    content = await resolve_atm_ivol(args)
    return content


@app.get('/prices/eod/conti')
async def conti_eod_prices(
        symbol: str, ust: str = 'fut', exchange: str = None, nthcontract: int = 1,
        startdate: str = None, enddate: str = None, dminus:  int = 20, order: str = 'asc'):
    args = {
        'symbol': symbol, 'ust': ust, 'exchange': exchange, 'nthcontract': nthcontract,
        'startdate': startdate, 'enddate': enddate,
        'dminus': dminus, 'order': order, 'array': 0
    }
    content = await conti_resolver(args)
    return content


@app.get('/prices/eod/conti/array')
async def conti_eod_prices(
    symbol: str, ust: str = 'fut', exchange: str = None,
    startdate: str = None, enddate: str = None, dminus:  int = 20, order: str = 'asc'):
    args = {
        'symbol': symbol, 'ust': ust, 'exchange': exchange,
        'startdate': startdate, 'enddate': enddate, 'dminus': dminus, 'order': order,
        'array': 1
    }
    content = await conti_array_resolver(args)
    return content


if __name__ == '__main__':
    import uvicorn
    uvicorn.run(app, host='0.0.0.0', port=5000)
