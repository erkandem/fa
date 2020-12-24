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
import fastapi
from fastapi.security import OAuth2PasswordBearer
from starlette.middleware.cors import CORSMiddleware

import appconfig
from appconfig import origins
from src.ivol_atm import router as atm_router
from src.intraday_prices import router as intraday_prices_router
from src.pvp import router as pvp_router
from src.conti_prices import router as conti_router
from src.regular_futures import router as eod_futures_router
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


MAJOR = 4
MINOR = 0
PATCH = 0
__version__ = f'{MAJOR}.{MINOR}.{PATCH}'


app = fastapi.FastAPI(
    # https://fastapi.tiangolo.com/advanced/extending-openapi/
    title='iVolAPI',
    version=__version__,
    description='implied volatility and price data for selected ETFs and futures. Contact: info at volsurf.com',
    docs_url='/',
    servers=appconfig.OPENAPI_SERVERS,
)

# API overhead
app.include_router(heartbeat_router, tags=['API Health'])

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
app.include_router(topoi_router, tags=['Composite', 'RawData'])
app.include_router(delta_router, tags=['Composite', 'RawData'])
app.include_router(risk_reversal_router, tags=['Composite', 'ImpliedVolatility'])
app.include_router(ivol_summary_statistics_router, tags=['Composite', 'ImpliedVolatility'])


oauth2_scheme = OAuth2PasswordBearer(tokenUrl='/token')

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
