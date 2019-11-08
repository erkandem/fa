from collections import namedtuple
from datetime import datetime as dt
from datetime import timedelta
import fastapi
from starlette.status import HTTP_200_OK
from falib.contract import Contract
from src.const import OrderChoices
from src.utils import guess_exchange_and_ust
from src.utils import eod_ini_logic
from src.db import engines
from src.users.auth import bouncer
from src.users.auth import get_current_active_user
from src.users.user_models import UserPy


router = fastapi.APIRouter()


@bouncer.roles_required('user')
@router.get(
    '/prices/intraday/pvp',
    operation_id='get_pvp_intraday',
    summary='price volume profile. histogram of intraday price data'
)
async def get_pvp_intraday(
        symbol: str, month: str = None, year: int = None,
        ust: str = None,
        exchange: str = None,
        startdate: str = None, enddate: str = None,
        dminus: int = 20,
        buckets: int = 100,
        iunit: str = 'minutes',
        order: OrderChoices = OrderChoices._asc,
        user: UserPy = fastapi.Depends(get_current_active_user)
):
    """
    price volume profile. histogram of intraday price data

    - **symbol**: example: 'SPY' or 'spy' (case insensitive)
    - **month**: only for futures - one of ['F', 'G', 'H', 'J', 'K', 'M', 'N', 'Q', 'U', 'V', 'X', 'Z']
    - **year**: only for futures - example: 19
    - **ust**: underlying security type: ['fut', 'eqt', 'ind', 'fx']
    - **exchange**: one of: ['usetf', 'cme', 'ice', 'eurex']
    - **startdate**: format: yyyymmdd
    - **enddate**: format: yyyymmdd
    - **dminus**: indicate the number of days back from `enddate`
    - **buckets**: number of intervals in the histogram
    - **iunit**: one of ['minutes', 'hour, 'day', 'week', 'month']
    - **order**:  sorting order with respect to price interval
    """
    args = {
        'symbol': symbol, 'month': month, 'year': year, 'ust': ust, 'exchange': exchange,
        'startdate': startdate, 'enddate': enddate, 'dminus': dminus,
        'buckets': buckets, 'iunit': iunit, 'order': order.value
    }
    content = await resolve_pvp(args)
    return content


pvpQueryParams = namedtuple(
    'pvpQueryParams',
    ['schema', 'table', 'startdate', 'enddate', 'buckets'])


async def pvp_query(args):
    """start_date end_date symbol c_month c_year exchange ust"""
    args = await guess_exchange_and_ust(args)
    c = Contract()
    c.symbol = args['symbol']
    c.exchange = args['exchange']
    c.security_type = args['ust']
    args = await eod_ini_logic(args)
    if args['year'] is not None:
        c.contract_yyyy = 2000 + args['year']
    if args['month'] is not None:
        c.contract_month = args['month']
    if c.contract_month and c.contract_yyyy:
        c.contract = f'''{args['symbol']}{args['month']}{args['year']}'''.lower()
    schema = await c.compose_2_part_schema_name()
    table = await c.compose_prices_intraday_table_name()
    params = pvpQueryParams(
        schema=schema, table=table,
        startdate=args['startdate'], enddate=args['enddate'],
        buckets=args['buckets']
    )
    sql = await final_sql(params)
    return sql


async def final_sql(nt: pvpQueryParams) -> str:
    return f'''

    WITH mima AS (
            SELECT    MIN(close_value) AS abs_min, 
                      MAX(close_value)  AS abs_max 
            FROM      {nt.schema}.{nt.table} 
            WHERE dt BETWEEN '{nt.startdate}' AND  '{nt.enddate}' 
        ) 
    SELECT  width_bucket(
                tab.close_value,
                    (SELECT abs_min FROM mima LIMIT 1),
                    (SELECT abs_max FROM mima LIMIT 1),
                    {nt.buckets}
                ) 
                AS bucket,
            SUM(tab.volume_value) AS sum_volume, 
            MIN(tab.close_value) AS min_close, 
            MAX(tab.close_value) AS max_close 
    FROM      {nt.schema}.{nt.table} tab 
    WHERE    tab.dt BETWEEN '{nt.startdate}' AND  '{nt.enddate}' 
    GROUP BY bucket 
    ORDER BY min_close; 
    '''


async def resolve_pvp(args):
    sql = await pvp_query(args)
    async with engines['prices'].acquire() as con:
        data = await con.fetch(query=sql)
        return data
