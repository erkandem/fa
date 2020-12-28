"""

"""
import fastapi
from starlette.middleware.cors import CORSMiddleware

import appconfig
from src.ivol_atm import router as atm_router
from src.prices_intraday import router as intraday_prices_router
from src.pvp import router as pvp_router
from src.prices_continuous import router as conti_router
from src.prices_regular_futures import router as eod_futures_router
from src.heartbeat import router as heartbeat_router
from src.ivol_surface_by_delta import router as surface_router
from src.rawoption_data import router as rawdata_router
from src.info import router as info_outer
from src.topoi_data import router as topoi_router
from src.delta_data import router as delta_router
from src.ivol_smile import router as smile_router
from src.ivol_risk_reversal import router as risk_reversal_router
from src.ivol_calendar_spread import router as calendar_router
from src.ivol_summary_statistics import router as ivol_summary_statistics_router
from src.ivol_inter_spread import router as ivol_inter_spread_router
from src.rawdata_all_options import router as all_options_single_day_router
from src.users import users_router, auth_router
from src.db import connect_async_engines, disconnect_async_engines, dispose_engines

MAJOR = 4
MINOR = 0
PATCH = 1
__version__ = f'{MAJOR}.{MINOR}.{PATCH}'


app = fastapi.FastAPI(
    title='ivolapi',
    version=__version__,
    description='implied volatility and price data for selected ETFs and futures. Contact: info at volsurf.com',
    docs_url='/',
    on_startup=[
        connect_async_engines,
    ],
    on_shutdown=[
        disconnect_async_engines,
        dispose_engines,
    ],
    servers=appconfig.OPENAPI_SERVERS,
)

# API overhead
app.include_router(heartbeat_router, tags=['API Health'])

# user related routers
app.include_router(users_router, tags=['User'])
app.include_router(auth_router, tags=['Login'])

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
app.include_router(all_options_single_day_router, tags=['RawData'])

# custom composite routes
app.include_router(topoi_router, tags=['Composite'])
app.include_router(delta_router, tags=['Composite'])
app.include_router(risk_reversal_router, tags=['Composite'])
app.include_router(ivol_summary_statistics_router, tags=['Composite'])


app.add_middleware(
    CORSMiddleware,
    allow_origins=appconfig.origins,
    allow_credentials=True,
    allow_methods=['*'],
    allow_headers=['*'],
)


if __name__ == '__main__':
    import uvicorn
    uvicorn.run(
        app,
        host=appconfig.IVOLAPI_HOST,
        port=appconfig.IVOLAPI_PORT,
        debug=appconfig.IVOLAPI_DEBUG,
    )
