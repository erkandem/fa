"""
http://0.0.0.0:5000/prices/intraday?symbol=ewz
http://0.0.0.0:5000/prices/eod/conti?symbol=cl
http://0.0.0.0:5000/prices/eod/conti/array?symbol=cl


http://0.0.0.0:5000/prices/intraday?symbol=ewz&startdate=20191001
http://0.0.0.0:5000/prices/intraday?symbol=ewz&startdate=20191001&interval=1&iunit=day

"""
from datetime import datetime as dt
from falib.db import engines, pgc
import asyncpg
from fastapi import FastAPI
from pydantic import BaseModel
from datetime import date
from src.conti_prices import conti_resolver
from src.conti_prices import conti_array_resolver
from src.conti_prices import ContiEodArray
from src.conti_prices import FuturesEodConti
from src.intraday_prices import prices_intraday_content
from src.intraday_prices import PricesIntraday

app = FastAPI()


@app.on_event('startup')
async def startup():
    engines['prices'] = await asyncpg.create_pool(pgc.get_uri('prices_intraday'))
    engines['dev'] = await asyncpg.create_pool(pgc.get_uri('pymarkets_null'))


@app.on_event('shutdown')
async def shutdown():
    await engines['prices'].close()
    await engines['dev'].close()


class Pulse(BaseModel):
    date: dt


@app.get('/', response_model=Pulse)
async def root():
    return {'date': dt.now()}


@app.get('/prices/intraday') # response_model=PricesIntraday
async def conti_eod_prices(
    symbol: str,
    month: int = None,
    year: int = None,
    ust: str = None,
    exc: str = None,
    startdate: str = None,
    enddate: str = None,
    interval: int = 1,
    iunit: str = 'minutes',
    dminus: int = 20,
    order: str = 'asc',
):
    args = {
        'symbol': symbol,
        'month': month,
        'year': year,
        'ust': ust,
        'exc': exc,
        'startdate': startdate,
        'enddate': enddate,
        'dminus': dminus,
        'interval': interval,
        'iunit': iunit,
        'order': order
    }
    content = await prices_intraday_content(args)
    return content


@app.get('/prices/eod/conti')  # response_model=FuturesEodConti
async def conti_eod_prices(
    symbol: str,
    exchange: str = None,
    startdate: str = None,
    enddate: str = None,
    dminus:  int = 20,
    order: str = 'asc',
    nthcontract: int = 1
):
    args = {
        'symbol': symbol,
        'exchange': exchange,
        'startdate': startdate,
        'enddate': enddate,
        'dminus': dminus,
        'order': order,
        'nthcontract': nthcontract,
        'ust': 'fut',
        'array': 0
    }
    content = await conti_resolver(args)
    return content


@app.get('/prices/eod/conti/array')  # response_model=ContiEodArray
async def conti_eod_prices(
    symbol: str,
    exchange: str = None,
    startdate: str = None,
    enddate: str = None,
    dminus:  int = 20,
    order: str = 'asc',
):
    args = {
        'symbol': symbol,
        'exchange': exchange,
        'startdate': startdate,
        'enddate': enddate,
        'dminus': dminus,
        'order': order,
        'ust': 'fut',
        'array': 1
    }
    content = await conti_array_resolver(args)
    return content


if __name__ == '__main__':
    import uvicorn
    uvicorn.run(app, host='0.0.0.0', port=5000)
