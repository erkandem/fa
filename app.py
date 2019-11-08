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
import asyncpg
import fastapi
from starlette.middleware.cors import CORSMiddleware
import databases
from appconfig import USERDB_URL
from src.db import engines, pgc
from src.users.users import create_initial_superuser

from src.atm import router as atm_router
from src.intraday_prices import router as intraday_prices_router
from src.pvp import router as pvp_router
from src.conti_prices import router as conti_router
from src.regular_futures import router as eod_futures_router
from src.pulse import router as pulse_router
from src.surfacebydelta import router as surface_router
from src.users.auth import router as auth_router
from src.users.content import router as content_router
from src.users.decorated_content import router as dc_router
from src.users.users import router as users_router
from src.users.db import table_creation

from fastapi import Depends, FastAPI
from fastapi.security import OAuth2PasswordBearer


app = fastapi.FastAPI(
    title='iVolAPI',
    version='2.0.1',
    description='implied volatility and price data for selected ETFs and futures',
    docs_url='/'
)

app.include_router(pulse_router)
app.include_router(atm_router)
app.include_router(surface_router)
app.include_router(intraday_prices_router)
app.include_router(pvp_router)
app.include_router(conti_router)
app.include_router(eod_futures_router)
app.include_router(auth_router, tags=['Auth'])
app.include_router(content_router, prefix='/content', tags=['Content'])
app.include_router(dc_router, prefix='/dc', tags=['Decorated Routes'])
app.include_router(users_router, tags=['Users'])


oauth2_scheme = OAuth2PasswordBearer(tokenUrl='/token')


@app.on_event('startup')
async def startup():
    engines['prices'] = await asyncpg.create_pool(pgc.get_uri('prices_intraday'))
    engines['dev'] = await asyncpg.create_pool(pgc.get_uri('pymarkets_null'))
    engines['t2'] = await asyncpg.create_pool(pgc.get_uri('pymarkets_tests_db_two'))
    engines['yh'] = await asyncpg.create_pool(pgc.get_uri('experimental_usyh_rawdata'))
    table_creation(USERDB_URL)
    engines['users'] = databases.Database(USERDB_URL)
    await engines['users'].connect()
    await create_initial_superuser()


@app.on_event('shutdown')
async def shutdown():
    await engines['prices'].close()
    await engines['dev'].close()
    await engines['t2'].close()
    await engines['experimental_usyh_rawdata'].close()
    await engines['users'].disconnect()


if __name__ == '__main__':
    import uvicorn
    uvicorn.run(app, host='0.0.0.0', port=5000)
