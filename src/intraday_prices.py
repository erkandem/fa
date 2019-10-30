from collections import namedtuple
from datetime import datetime as dt
from datetime import date
from datetime import timedelta

from falib.const import ust_choices_intraday
from falib.const import exchange_choices_intraday
from falib.const import futures_month_chars
from falib.const import prices_intraday_all_symbols
from falib.utils import eod_ini_logic
from falib.utils import guess_exchange_and_ust
from falib.contract import Contract
from falib.db import engines
from pydantic import BaseModel
import fastapi
from starlette.status import HTTP_200_OK
from falib.const import OrderChoices

router = fastapi.APIRouter()

prices_intraday_keys = [
    'symbol',
    'month',
    'year',
    'ust',
    'exc',
    'startdate',
    'enddate',
    'dminus',
    'interval',
    'iunit',
    'order'
 ]


class PricesIntraday(BaseModel):
    dt: dt
    tz: int
    open: float
    high: float
    low: float
    close: float
    volume: int


class PricesIntradayQuery(BaseModel):
    symbol: str
    month: str
    year: int
    ust: str
    exchange: str
    startdate: date
    enddate: date
    dminus: int
    interval: int
    iunit: str
    order: str


class Validator:
    @staticmethod
    async def interval(x): return x in [1, 2, 5, 10, 15]
    @staticmethod
    async def interval_unit(x): return x in ['minutes', 'hour', 'day', 'week']
    @staticmethod
    async def order(x): return x.lower() in ['asc', 'desc']
    @staticmethod
    async def symbols(x): return x.lower() in prices_intraday_all_symbols
    @staticmethod
    async def month(x): return x.lower() in futures_month_chars
    @staticmethod
    async def exchange(x): return x.lower() in exchange_choices_intraday
    @staticmethod
    async def ust(x): return x.lower() in ust_choices_intraday


v = Validator()


IntradayPricesParams = namedtuple('IntradayPricesParams', [
    'schema', 'table',
    'interval', 'multi',
    'startdate', 'enddate',
    'order',
    'limit'
])


@router.get('/prices/intraday', status_code=HTTP_200_OK)
async def conti_eod_prices(
        symbol: str, month: int = None, year: int = None, ust: str = None, exchange: str = None,
        startdate: str = None, enddate: str = None, dminus: int = 20,
        interval: int = 1, iunit: str = 'minutes',
        order: OrderChoices = OrderChoices._asc
):
    args = {
        'symbol': symbol, 'month': month, 'year': year, 'ust': ust, 'exchange': exchange,
        'startdate': startdate, 'enddate': enddate, 'dminus': dminus,
        'interval': interval, 'iunit': iunit, 'order': order.value
    }
    content = await prices_intraday_content(args)
    return content

async def select_prices_intraday(args: dict):
    """return an executable SQL statement"""
    args = await guess_exchange_and_ust(args)
    c = Contract()
    c.symbol = args['symbol']
    c.exchange = args['exchange']
    c.security_type = args['ust']
    if args['year'] is not None:
        c.contract_yyyy = 2000 + args['year']
    if args['month'] is not None:
        c.contract_month = args['month']
    if c.contract_month and c.contract_yyyy:
        c.contract = f'''{args['symbol']}{args['month']}{args['year']}'''.lower()
    args = await eod_ini_logic(args)
    schema = await c.compose_2_part_schema_name()
    table = await c.compose_prices_intraday_table_name()
    limit = 260
    multi = 60
    interval = args['iunit']

    sc_flag = False
    if args['interval'] == 1:
        sc_flag = True
    else:
        if args['iunit'] == 'month':
            sc_flag = True
        elif args['iunit'] == 'week':
            sc_flag = True
        elif args['iunit'] == 'day':
            sc_flag = True
        elif args['iunit'] == 'hour':
            multi = 60 * 60 * args['interval']
        elif args['iunit'] == 'minutes':
            multi = 60 * args['interval']

    sql_params = IntradayPricesParams(
        schema=schema,
        table=table,
        interval=interval,
        multi=multi,
        startdate=args['startdate'],
        enddate=args['enddate'],
        order=args['order'],
        limit=limit
    )
    sql_code = await __cast_to_sql(sql_params, sc_flag=sc_flag)
    return sql_code


async def __cast_to_sql(args: IntradayPricesParams, *, sc_flag: bool):
    if sc_flag:
        sql = await __cast_to_sql_b(args)
    else:
        sql = await __cast_to_sql_a(args)
    return sql


async def __cast_to_sql_a(nt: IntradayPricesParams) -> str:
    """ case, where we truncate personally"""
    return f'''
    SELECT (to_timestamp(floor((extract('epoch' FROM dt) / {nt.multi})) * {nt.multi}) AT TIME ZONE 'UTC')  AS dt, 
           MAX(tz_offset)                                  AS tz, 
           (array_agg(open_value ORDER BY dt ASC)) [1]     AS open, 
           MAX(high_value)                                 AS high, 
           MIN(low_value)                                  AS low, 
           (array_agg(close_value ORDER BY dt DESC))[1]    AS close,  
           SUM(volume_value)                               AS volume 
    FROM   {nt.schema}.{nt.table} 
    WHERE  dt BETWEEN '{nt.startdate}' AND '{nt.enddate}' 
    GROUP BY floor(extract('epoch' FROM dt) / {nt.multi})  
    ORDER BY dt  {nt.order}  
    LIMIT {nt.limit}; 
    '''


async def __cast_to_sql_b(nt: IntradayPricesParams) -> str:
    """case, where the database takes care truncating by date"""
    return f'''
        SELECT   date_trunc('{nt.interval}', dt)                    AS dt, 
                 MAX(tz_offset)                                  AS tz, 
                 (array_agg(open_value ORDER BY dt ASC))[1]      AS open, 
                 MAX(high_value)                                 AS high, 
                 MIN(low_value)                                  AS low, 
                 (array_agg(close_value ORDER BY dt DESC))[1]    AS close, 
                 SUM(volume_value)                               AS volume 
        FROM     {nt.schema}.{nt.table} 
        WHERE    dt BETWEEN '{nt.startdate}' AND '{nt.enddate}' 
        GROUP BY date_trunc('{nt.interval}', dt) 
        ORDER BY dt  {nt.order} 
        LIMIT    {nt.limit}; 
         '''


async def prices_intraday_content(args):
    sql = await select_prices_intraday(args)
    async with engines['prices'].acquire() as con:
        data = await con.fetch(query=sql)
        return data
