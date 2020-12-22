from datetime import datetime as dt
from datetime import date as Date
import fastapi
from pydantic import BaseModel
from starlette.status import HTTP_400_BAD_REQUEST
from starlette.status import HTTP_500_INTERNAL_SERVER_ERROR
from falib.contract import Contract
from src.const import OrderChoices
from src.utils import eod_ini_logic_new
from src.utils import guess_exchange_and_ust
from appconfig import engines
from src.const import IntervalUnitChoices, IntervalValueChoices
from starlette.exceptions import HTTPException
import json

router = fastapi.APIRouter()


allowed_queries_configs = {
    'month_1': {'unit': 'month', 'value': 1, 'query': 'date_trunc', 'multiplier': None},
    'week_1': {'unit': 'week', 'value': 1, 'query': 'date_trunc', 'multiplier': None},
    'day_1': {'unit': 'day', 'value': 1, 'query': 'date_trunc', 'multiplier': None},
    'hour_2': {'unit': 'hour', 'value': 2, 'query': 'floor_extract', 'multiplier': 60 * 60 * 2},
    'hour_1': {'unit': 'hour', 'value': 1, 'query': 'date_trunc', 'multiplier': None},
    'minutes_30': {'unit': 'minutes', 'value': 30, 'query': 'floor_extract', 'multiplier': 60 * 30},
    'minutes_20': {'unit': 'minutes', 'value': 20, 'query': 'floor_extract', 'multiplier': 60 * 20},
    'minutes_15': {'unit': 'minutes', 'value': 15, 'query': 'floor_extract', 'multiplier': 60 * 15},
    'minutes_10': {'unit': 'minutes', 'value': 10, 'query': 'floor_extract', 'multiplier': 60 * 10},
    'minutes_5': {'unit': 'minutes', 'value': 5, 'query': 'floor_extract', 'multiplier': 60 * 5},
    'minutes_4': {'unit': 'minutes', 'value': 4, 'query': 'floor_extract', 'multiplier': 60 * 4},
    'minutes_3': {'unit': 'minutes', 'value': 3, 'query': 'floor_extract', 'multiplier': 60 * 3},
    'minutes_2': {'unit': 'minutes', 'value': 2, 'query': 'floor_extract', 'multiplier': 60 * 2},
    'minutes_1': {'unit': 'minutes', 'value': 1, 'query': 'regular', 'multiplier': None}
 }

allowed_queries = list(allowed_queries_configs)
unique_units = list(set([elm['unit'] for elm in allowed_queries_configs.values()]))
valid_configs = {
    unit: [
        elm['value']
        for elm in allowed_queries_configs.values()
        if elm['unit'] == unit
        ] for unit in unique_units
}
valid_configs_json = json.dumps(valid_configs)


class PricesIntradayPy(BaseModel):
    dt: dt
    tz: int
    open: float
    high: float
    low: float
    close: float
    volume: int


class PricesIntradayQueryPy(BaseModel):
    symbol: str
    month: str
    year: int
    ust: str
    exchange: str
    startdate: Date
    enddate: Date
    dminus: int
    interval: int
    iunit: str
    order: str


@router.get(
    '/prices/intraday',
    operation_id='get_intraday_prices'
)
async def get_intraday_prices(
        symbol: str,
        month: str = None,
        year: int = None,
        ust: str = None,
        exchange: str = None,
        startdate: Date = None,
        enddate: Date = None,
        dminus: int = 20,
        interval: IntervalValueChoices = IntervalValueChoices._1,
        iunit: IntervalUnitChoices = IntervalUnitChoices._minutes,
        order: OrderChoices = OrderChoices._asc,
):
    args = {
        'symbol': symbol,
        'month': month,
        'year': year,
        'ust': ust,
        'exchange': exchange,
        'startdate': startdate,
        'enddate': enddate,
        'dminus': dminus,
        'interval': interval.value,
        'iunit': iunit.value,
        'order': order.value,
        'limit': 365 * 2
    }
    content = await resolve_prices_intraday(args)
    return content


async def select_prices_intraday(args: dict):
    """return an executable SQL statement"""
    args = await eod_ini_logic_new(args)
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

    args['schema'] = await c.compose_2_part_schema_name()
    args['table'] = await c.compose_prices_intraday_table_name()
    sql_code = await select_price_data(args)
    return sql_code


async def _create_hash(unit, interval):
    return f'{unit}_{interval}'


async def select_price_data(args):
    hash = await _create_hash(args['iunit'], args['interval'])
    if hash not in allowed_queries:
        raise HTTPException(
            status_code=HTTP_400_BAD_REQUEST,
            detail=f"received unit: `{args['iunit']}` and interval `{args['interval']}`. Valid pairs are: {valid_configs}")
    details = allowed_queries_configs[hash]
    args['multiplier'] = details['multiplier']
    if details['query'] == 'floor_extract':
        sql = await select_via_floor_extract(args)
    elif details['query'] == 'date_trunc':
        sql = await select_via_date_trunc(args)
    elif details['query'] == 'regular':
        sql = await select_regular(args)
    else:
        raise HTTPException(
            status_code=HTTP_500_INTERNAL_SERVER_ERROR,
            detail='We fucked up.'
        )
    return sql


async def select_via_floor_extract(args) -> str:
    """case, where we truncate low level by converting datetime to epochs"""
    return f'''
    SELECT (to_timestamp(
                floor((extract('epoch' FROM dt) / {args['multiplier']}))
                 * {args['multiplier']}
            ) AT TIME ZONE 'UTC')                          AS dt, 
           MAX(tz_offset)                                  AS tz, 
           (array_agg(open_value ORDER BY dt)) [1]         AS open, 
           MAX(high_value)                                 AS high, 
           MIN(low_value)                                  AS low, 
           (array_agg(close_value ORDER BY dt DESC))[1]    AS close,  
           SUM(volume_value)                               AS volume 
    FROM   {args['schema']}.{args['table']} 
    WHERE  dt BETWEEN '{args['startdate']}' AND '{args['enddate']}' 
    -- create one integers (although double) for each row
    -- same like date_trunc() creates unqiue timestamps only with integers**
    GROUP BY floor(extract('epoch' FROM dt) / {args['multiplier']})  
    ORDER BY dt  {args['order']}  
    LIMIT {args['limit']}; 
    '''


async def select_via_date_trunc(args) -> str:
    """
    case, where the database takes care of truncating data by date
    """
    return f'''
        SELECT   date_trunc('{args['iunit']}', dt)                    AS dt, 
                 MAX(tz_offset)                                  AS tz, 
                 (array_agg(open_value ORDER BY dt ASC))[1]      AS open, 
                 MAX(high_value)                                 AS high, 
                 MIN(low_value)                                  AS low, 
                 (array_agg(close_value ORDER BY dt DESC))[1]    AS close, 
                 SUM(volume_value)                               AS volume 
        FROM     {args['schema']}.{args['table']} 
        WHERE    dt BETWEEN '{args['startdate']}' AND '{args['enddate']}' 
        GROUP BY date_trunc('{args['iunit']}', dt)
        ORDER BY dt  {args['order']} 
        LIMIT    {args['limit']};'''


async def select_regular(args) -> str:
    """
    case, where unit = minute and value = 1
    """
    return f'''
        SELECT   dt AS dt,
                 tz_offset AS tz, 
                 open_value AS open, 
                 high_value AS high, 
                 low_value AS low, 
                 close_value AS close, 
                 volume_value AS volume 
        FROM     {args['schema']}.{args['table']} 
        WHERE    dt BETWEEN '{args['startdate']}' AND '{args['enddate']}' 
        ORDER BY dt  {args['order']} 
        LIMIT    {args['limit']};'''


async def resolve_prices_intraday(args):
    sql = await select_prices_intraday(args)
    async with engines.prices_intraday.acquire() as con:
        data = await con.fetch(query=sql)
        return data
