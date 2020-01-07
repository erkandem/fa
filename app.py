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
import databases
import fastapi
from fastapi.security import OAuth2PasswordBearer
from starlette.middleware.cors import CORSMiddleware
from appconfig import USERDB_URL
from appconfig import USERDB_URL_PG
from src.db import engines, pgc
from src.users.users import create_initial_superuser
from src.users.users import create_other_default_user
from src.ivol_atm import router as atm_router
from src.intraday_prices import router as intraday_prices_router
from src.pvp import router as pvp_router
from src.conti_prices import router as conti_router
from src.regular_futures import router as eod_futures_router
from src.heartbeat import router as heartbeat_router
from src.ivol_surface_by_delta import router as surface_router
from src.rawoption_data import router as rawdata_router
from src.users.auth import router as auth_router
from src.users.content import router as content_router
from src.users.decorated_content import router as dc_router
from src.users.users import router as users_router
from src.users.db import table_creation
from src.info import router as info_outer
from src.topoi_data import router as topoi_router
from src.delta_data import router as delta_router
from src.ivol_smile import router as smile_router
from src.ivol_risk_reversal import router as risk_reversal_router
from src.ivol_calendar_spread import router as calendar_router
from src.ivol_summary_statistics import router as ivol_summary_statistics_router
from src.ivol_inter_spread import router as ivol_inter_spread_router


MAJOR = 3
MINOR = 0
PATCH = 0
__version__ = f'{MAJOR}.{MINOR}.{PATCH}'


app = fastapi.FastAPI(
    title='iVolAPI',
    version=__version__,
    description='implied volatility and price data for selected ETFs and futures',
    docs_url='/'
)

# API overhead
app.include_router(heartbeat_router, tags=['API Health'])
app.include_router(users_router, tags=['Users'])
app.include_router(auth_router, tags=['Auth'])

# implied volatility routes
app.include_router(atm_router, tags=['ImpliedVolatility'])
app.include_router(smile_router, tags=['ImpliedVolatility'])
app.include_router(surface_router, tags=['ImpliedVolatility'])
app.include_router(calendar_router, tags=['ImpliedVolatility'])
app.include_router(ivol_inter_spread_router, tags=['ImpliedVolatility'])

# price data
app.include_router(intraday_prices_router, tags=['PriceData'])
app.include_router(pvp_router, tags=['PriceData'])
app.include_router(conti_router, tags=['PriceData'])
app.include_router(eod_futures_router, tags=['PriceData'])

# raw data
app.include_router(rawdata_router, tags=['RawData'])
app.include_router(info_outer, prefix='/info', tags=['Info'])

# custom composite routes
app.include_router(topoi_router, tags=['Composite', 'RawData'])
app.include_router(delta_router, tags=['Composite', 'RawData'])
app.include_router(risk_reversal_router, tags=['Composite', 'ImpliedVolatility'])
app.include_router(ivol_summary_statistics_router, tags=['Composite', 'ImpliedVolatility'])

# auth testing routes, which are removed from the documentation
app.include_router(content_router, prefix='/content', tags=['Content'])
app.include_router(dc_router, prefix='/dc', tags=['Decorated Routes'])


oauth2_scheme = OAuth2PasswordBearer(tokenUrl='/token')

st_counter = '''
    <!-- Default Statcounter code for Api.volsurf.com https://api.volsurf.com -->
        <script type="text/javascript">
            var sc_project=12144901; 
            var sc_invisible=1; 
            var sc_security="b6ffef77"; 
        </script>
        <script type="text/javascript" src="https://www.statcounter.com/counter/counter.js" async></script>
        <noscript>
            <div class="statcounter">
                <a title="Web Analytics" href="https://statcounter.com/" target="_blank">
                    <img class="statcounter" src="https://c.statcounter.com/12144901/0/b6ffef77/1/" alt="Web Analytics">
                </a>
            </div>
        </noscript>
    <!-- End of Statcounter Code -->
'''

origins = [
    'http://api.volsurf.com',
    'https://api.volsurf.com',
    'http:localhost',
    'http:localhost:5000',
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=['*'],
    allow_headers=['*'],
)


@app.on_event('startup')
async def startup():
    engines['prices_intraday'] = await asyncpg.create_pool(pgc.get_uri('prices_intraday'))
    engines['pgivbase'] = await asyncpg.create_pool(pgc.get_uri('pgivbase'))
    engines['options_rawdata'] = await asyncpg.create_pool(pgc.get_uri('options_rawdata'))
    table_creation(USERDB_URL)
    engines['users'] = databases.Database(USERDB_URL)
    await engines['users'].connect()
    await create_initial_superuser()
    await create_other_default_user()


@app.on_event('shutdown')
async def shutdown():
    await engines['prices_intraday'].close()
    await engines['pgivbase'].close()
    await engines['options_rawdata'].close()
    await engines['users'].disconnect()


if __name__ == '__main__':
    import uvicorn
    uvicorn.run(app, host='0.0.0.0', port=5000)
