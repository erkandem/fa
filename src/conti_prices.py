from pydantic import BaseModel
from datetime import datetime as dt
from collections import namedtuple
from datetime import datetime as dt
from datetime import date
from datetime import timedelta

from falib.const import nth_contract_choices
from falib.const import conti_futures_choices
from falib.utils import add_missing_keys
from falib.utils import guess_exchange_from_symbol_intraday
from falib.contract import Contract
from falib.db import engines


class Validator:
    @staticmethod
    def order(x): return x.lower() in ['asc', 'desc']
    @staticmethod
    def symbols(x): return x.lower() in conti_futures_choices
    @staticmethod
    def exchange(x): return x.lower() in ['cme', 'ice']
    @staticmethod
    def dminus(x): return 1 < x < 365
    @staticmethod
    def nth_contract(x): return x in nth_contract_choices


v = Validator()

query_keys = [
    'symbol',
    'exchange',
    'startdate',
    'enddate',
    'dminus',
    'order',
    'nthcontract'
]


class ContiEodQuery(BaseModel):
    symbol = str
    exchange = str
    startdate = date
    enddate = date
    dminus = int
    order = str
    nthcontract = int


class FuturesEodConti(BaseModel):
    dt = dt
    open = float
    high = float
    low = float
    close = float
    volume = int
    oi = int


class ContiEodArray(BaseModel):
    dt = dt
    c1 = float
    c2 = float
    c3 = float
    c4 = float
    c5 = float
    c6 = float
    c7 = float
    c8 = float
    c9 = float
    c10 = float
    c11 = float
    c12 = float


async def create_conti_eod_table_name(
        symbol: str,
        security_type: str,
        exchange: str,
        *,
        contract_number: int = None,
        nth_contract: str = None
) -> str:
    if nth_contract is None and contract_number is None:
        raise ValueError('It\'s got to be one of them')
    elif nth_contract is None and contract_number is not None:
        nth_contract = f'{symbol}{contract_number}'
    elif nth_contract is not None and contract_number is not None:
        raise ValueError('Make up your mind')
    elif nth_contract is not None and contract_number is None:
        nth_contract = nth_contract
    return (f'{security_type}'
            f'_{exchange}'
            f'_{nth_contract}'
            f'_prices_eod_conti').lower()


async def create_conti_eod_array_table_name(
        symbol: str,
        security_type: str,
        exchange: str,
) -> str:
    return (f'{security_type}'
            f'_{exchange}'
            f'_{symbol}'
            f'_prices_eod_conti_array').lower()


async def create_conti_eod_schema_name(security_type: str, exchange: str) -> str:
    return (f'{security_type}'
            f'_{exchange}'
            f'_eod_conti').lower()


async def eod_continuous_fut_sql_delivery(args):
    args = await add_missing_keys(query_keys, args)
    args['exchange'] = await guess_exchange_from_symbol_intraday(args['symbol'])
    delta_d = timedelta(days=args['dminus'])
    if args['enddate'] is None:
        args['enddate'] = (dt.now()).strftime('%Y%m%d')
    elif args['enddate'] is str:
        args['enddate'] = dt.strptime(args['enddate'], '%Y%m%d').strftime('%Y-%m-%d')
    if args['startdate'] is None:
        args['startdate'] = (dt.strptime(args['enddate'], '%Y%m%d') - delta_d).strftime('%Y-%m-%d')
    elif type(args['startdate']) is str:
        args['startdate'] = dt.strptime(args['startdate'], '%Y%m%d').strftime('%Y-%m-%d')
    schema = await create_conti_eod_schema_name(args['ust'], args['exchange'])
    table = await create_conti_eod_table_name(
        symbol=args['symbol'],
        security_type=args['ust'],
        exchange=args['exchange'],
        contract_number=args['nthcontract']
    )
    limit = 365
    sql = f'''
        SELECT * 
        FROM {schema}.{table} 
        WHERE dt  BETWEEN '{args['startdate']}' AND '{args['enddate']}' 
        ORDER BY dt {args['order']} 
        LIMIT {limit}; 
    '''
    return sql


async def eod_continuous_fut_array_sql_delivery(args: dict):
    args = await add_missing_keys(query_keys, args)
    args['exchange'] = await guess_exchange_from_symbol_intraday(args['symbol'])
    delta_d = timedelta(days=args['dminus'])
    if args['enddate'] is None:
        args['enddate'] = (dt.now()).strftime('%Y%m%d')
    elif args['enddate'] is str:
        args['enddate'] = dt.strptime(args['enddate'], '%Y%m%d').strftime('%Y-%m-%d')
    if args['startdate'] is None:
        args['startdate'] = (dt.strptime(args['enddate'], '%Y%m%d') - delta_d).strftime('%Y-%m-%d')
    elif type(args['startdate']) is str:
        args['startdate'] = dt.strptime(args['startdate'], '%Y%m%d').strftime('%Y-%m-%d')
    schema = await create_conti_eod_schema_name(args['ust'], args['exchange'])
    table = await create_conti_eod_array_table_name(
        symbol=args['symbol'],
        security_type=args['ust'],
        exchange=args['exchange']
    )
    limit = 365
    sql = f'''
       SELECT * 
       FROM {schema}.{table} 
       WHERE dt  BETWEEN '{args['startdate']}' AND '{args['enddate']}'
       ORDER BY dt {args['order']} 
       LIMIT {limit};
    '''
    return sql


async def conti_resolver(args):
    sql = await eod_continuous_fut_sql_delivery(args)
    async with engines['dev'].acquire() as con:
        data = await con.fetch(query=sql)
        return data


async def conti_array_resolver(args: dict):
    sql = await eod_continuous_fut_array_sql_delivery(args)
    async with engines['dev'].acquire() as con:
        data = await con.fetch(query=sql)
        return data
