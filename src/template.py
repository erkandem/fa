"""
Route template

"""
from collections import namedtuple
from datetime import datetime as dt
from datetime import date
from datetime import timedelta
import fastapi
from fastapi import Depends
from sqlalchemy.orm import Session

from falib.contract import ContractSync
from src.const import OrderChoices
from src.const import tteChoices
from starlette.status import HTTP_400_BAD_REQUEST
from src.utils import guess_exchange_and_ust
from src.utils import eod_ini_logic_new
from src.utils import CinfoQueries
from src.db import get_prices_intraday_db, get_options_rawdata_db, get_pgivbase_db, get_users_db

from starlette.responses import Response
from src.const import time_to_var_func
from src.users import get_current_active_user, User


router = fastapi.APIRouter()


@router.get(
    '/route/me/please',
    summary='<summary>',
    operation_id='unique_operation_id>'
)
async def unique_operation_id(
        symbol: str,
        ust: str = None,
        exchange: str = None,
        tte: tteChoices = tteChoices._1m,
        startdate: str = None,
        enddate: str = None,
        dminus: int = 30,
        order: OrderChoices = OrderChoices._asc,
        con: Session = Depends(get_options_rawdata_db),
        user: User = Depends(get_current_active_user),

):
    """
    A route template. Will set appropriate headers and forward
    the already serialized postgres response.

    - **symbol**: example: 'SPY' or 'spy' (case insensitive)
    - **ust**: underlying security type: 'eqt' e.g.
    - **exchange**: one of: 'usetf', e.g.
    - **tte**: time until expiry. 1m 3m 12m ...
    - **startdate**: format: yyyymmdd
    - **enddate**: format: yyyymmdd
    - **dminus**: indicate the number of days back from `enddate`
    - **order**:  sorting order with respect to date
    """
    args = {
        'symbol': symbol,
        'ust': ust,
        'exchange': exchange,
        'tte': tte.value,
        'startdate': startdate,
        'enddate': enddate,
        'dminus': dminus,
        'order': order.value
    }
    content = await resolve_me(args)
    return Response(content=content, media_type='application/json')


async def select_resolve(args):
    args = eod_ini_logic_new(args)
    args = guess_exchange_and_ust(args)
    sql = f'''
    WITH data AS (
        SELECT 1
    )
    SELECT json_agg(data) FROM data;
    '''
    return sql


async def resolve_me(args):
    sql = await select_resolve(args)
    async with engines.DATABASE_NAME.acquire() as con:
        data = await con.fetch(sql)
        if len(data) != 0:
            return data[0].get('json_agg')
        else:
            return '[]'
