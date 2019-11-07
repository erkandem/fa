from collections import namedtuple
from datetime import datetime as dt
from datetime import date
from datetime import timedelta
from typing import List
import fastapi
from pydantic import BaseModel
from starlette.status import HTTP_200_OK
from falib.contract import Contract
from src.const import OrderChoices
from src.const import nth_contract_choices
from src.const import conti_futures_choices
from src.utils import guess_exchange_and_ust
from src.utils import eod_ini_logic
from src.db import engines


router = fastapi.APIRouter()

ContiEodParams = namedtuple(
    'ContiEodParams',
    ['schema', 'table', 'startdate', 'enddate', 'order', 'limit']
)


class Validator:
    @staticmethod
    async def order(x): return x.lower() in ['asc', 'desc']
    @staticmethod
    async def symbols(x): return x.lower() in conti_futures_choices
    @staticmethod
    async def exchange(x): return x.lower() in ['cme', 'ice']
    @staticmethod
    async def dminus(x): return 1 < x < 365
    @staticmethod
    async def nth_contract(x): return x in nth_contract_choices


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
    symbol: str
    ust: str
    exchange: str
    nthcontract: int
    startdate: date
    enddate: date
    dminus: int
    order: str


class FuturesEodConti(BaseModel):
    dt: dt
    open: float
    high: float
    low: float
    close: float
    volume: int
    oi: int


class ContiEodArray(BaseModel):
    dt: dt
    c1: float
    c2: float
    c3: float
    c4: float
    c5: float
    c6: float
    c7: float
    c8: float
    c9: float
    c10: float
    c11: float
    c12: float


@router.get(
    '/prices/eod/conti',
    operation_id='get_continuous_eod'
)
async def get_conti_eod(
        symbol: str, ust: str = 'fut', exchange: str = None, nthcontract: int = 1,
        startdate: str = None, enddate: str = None, dminus:  int = 20,
        order: OrderChoices = OrderChoices._asc
):
    args = {
        'symbol': symbol, 'ust': ust, 'exchange': exchange, 'nthcontract': nthcontract,
        'startdate': startdate, 'enddate': enddate,
        'dminus': dminus,
        'order': order.value, 'array': 0
    }
    content = await conti_resolver(args)
    return content


@router.get(
    '/prices/eod/conti/array',
    operation_id='get_continuous_eod_as_array'
)
async def get_continuous_eod_as_array(
    symbol: str, ust: str = 'fut', exchange: str = None,
    startdate: str = None, enddate: str = None, dminus:  int = 20,
    order: OrderChoices = OrderChoices._asc
):
    args = {
        'symbol': symbol, 'ust': ust, 'exchange': exchange,
        'startdate': startdate, 'enddate': enddate, 'dminus': dminus,
        'order': order.value,
        'array': 1
    }
    content = await conti_array_resolver(args)
    return content


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
    args = await guess_exchange_and_ust(args)
    args = await eod_ini_logic(args)
    schema = await create_conti_eod_schema_name(args['ust'], args['exchange'])
    table = await create_conti_eod_table_name(
        symbol=args['symbol'],
        security_type=args['ust'],
        exchange=args['exchange'],
        contract_number=args['nthcontract']
    )
    limit = 365
    sql = await select_all_from(
        ContiEodParams(
            schema=schema,
            table=table,
            startdate=args['startdate'],
            enddate=args['enddate'],
            order=args['order'],
            limit=limit
        )
    )
    return sql


async def eod_continuous_fut_array_sql_delivery(args: dict):
    args = await guess_exchange_and_ust(args)
    args = await eod_ini_logic(args)
    schema = await create_conti_eod_schema_name(args['ust'], args['exchange'])
    table = await create_conti_eod_array_table_name(
        symbol=args['symbol'],
        security_type=args['ust'],
        exchange=args['exchange']
    )
    limit = 365
    params = ContiEodParams(
        schema=schema, table=table,
        startdate=args['startdate'], enddate=args['enddate'],
        order=args['order'],
        limit=limit
    )
    sql = await select_all_from(params)
    return sql


async def select_all_from(nt: ContiEodParams) -> str:
    return f'''
       SELECT * 
       FROM {nt.schema}.{nt.table} 
       WHERE dt  BETWEEN '{nt.startdate}' AND '{nt.enddate}'
       ORDER BY dt {nt.order} 
       LIMIT {nt.limit};
    '''


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
