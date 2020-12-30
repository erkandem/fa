from collections import namedtuple
from datetime import date
import typing as t

import fastapi
from fastapi import Depends
from fastapi.responses import ORJSONResponse
from pydantic import BaseModel
from sqlalchemy.orm.session import Session

from src.const import (
    OrderChoices,
    conti_futures_choices,
    nth_contract_choices,
)
from src.db import get_prices_intraday_db
from src.users import (
    User,
    get_current_active_user,
)
from src.utils import (
    eod_ini_logic_new,
    guess_exchange_and_ust,
)

router = fastapi.APIRouter()

ContiEodParams = namedtuple(
    'ContiEodParams',
    [
        'schema',
        'table',
        'startdate',
        'enddate',
        'order',
        'limit',
    ]
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
    dt: date
    open: float
    high: float
    low: float
    close: float
    volume: int
    oi: int


class FuturesEodContiSpread(BaseModel):
    dt: date
    value: float


class ContiEodArray(BaseModel):
    dt: date
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
    operation_id='get_continuous_eod',
    response_model=t.List[FuturesEodConti],
    response_class=ORJSONResponse,
)
async def get_conti_eod(
        symbol: str,
        ust: str = 'fut',
        exchange: str = None,
        nthcontract: int = 1,
        startdate: date = None,
        enddate: date = None,
        dminus:  int = 20,
        order: OrderChoices = OrderChoices._asc,
        con: Session = Depends(get_prices_intraday_db),
        user: User = Depends(get_current_active_user),
):
    """
    return the time series data for the n-th contract in line.

    Continues contracts are synthetic (i.e. non-tradable) futures contracts.
    The values are calculates by rolling the the future at specified time.

    Only available for futures.
    """
    args = {
        'symbol': symbol,
        'ust': ust,
        'exchange': exchange,
        'nthcontract': nthcontract,
        'startdate': startdate,
        'enddate': enddate,
        'dminus': dminus,
        'order': order.value,
        'array': 0
    }
    content = await conti_resolver(args, con)
    return content


@router.get(
    '/prices/eod/conti/spread',
    operation_id='get_continuous_eod_spread',
    response_model=t.List[FuturesEodContiSpread],
    response_class=ORJSONResponse,
)
async def get_continuous_eod_spread(
        symbol: str,
        ust: str = 'fut',  # TODO: only futures is actually supported
        exchange: str = None,
        nthcontract1: int = 1,
        nthcontract2: int = 2,
        startdate: date = None,
        enddate: date = None,
        dminus:  int = 20,
        order: OrderChoices = OrderChoices._asc,
        con: Session = Depends(get_prices_intraday_db),
        user: User = Depends(get_current_active_user),
):
    """ return the (price) spread for an underlying between the x-th and n-th continues future"""
    args = {
        'symbol': symbol,
        'ust': ust,
        'exchange': exchange,
        'nthcontract1': nthcontract1,
        'nthcontract2': nthcontract2,
        'startdate': startdate,
        'enddate': enddate,
        'dminus': dminus,
        'order': order.value,
        'array': 0,
    }
    content = await resolve_conti_spread(args, con)
    return content


@router.get(
    '/prices/eod/conti/array',
    operation_id='get_continuous_eod_as_array',
    response_model=t.List[ContiEodArray],
    response_class=ORJSONResponse,
)
async def get_continuous_eod_as_array(
        symbol: str,
        ust: str = 'fut',
        exchange: str = None,
        startdate: date = None,
        enddate: date = None,
        dminus:  int = 20,
        order: OrderChoices = OrderChoices._asc,
        con: Session = Depends(get_prices_intraday_db),
        user: User = Depends(get_current_active_user),
):
    """
    return the (price) spread of continues futures, compared to the first in line.
    The results are returned for 12 available continuous futures.
    """
    args = {
        'symbol': symbol,
        'ust': ust,
        'exchange': exchange,
        'startdate': startdate,
        'enddate': enddate,
        'dminus': dminus,
        'order': order.value,
        'array': 1,
    }
    content = await conti_array_resolver(args,  con)
    return content


async def create_conti_eod_table_name(
        symbol: str,
        security_type: str,
        exchange: str,
        *,
        contract_number: int = None,
        nth_contract: str = None
) -> str:
    """

    TODO: `create_conti_eod_table_name` needs to merged to the `Contract` class'
    """
    if nth_contract is None and contract_number is None:
        raise ValueError('It\'s got to be one of `nth_contract` or `contract_number`')
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
    """
    TODO: `create_conti_eod_array_table_name` needs to merged to the `Contract` class'
    """
    return (
        f'{security_type}'
        f'_{exchange}'
        f'_{symbol}'
        f'_prices_eod_conti_array'
    ).lower()


async def create_conti_eod_schema_name(security_type: str, exchange: str) -> str:
    """
    TODO: `create_conti_eod_schema_name` needs to merged to the `Contract` class'
    """
    return (f'{security_type}'
            f'_{exchange}'
            f'_eod_conti').lower()


async def eod_continuous_fut_sql_delivery(args):
    args = eod_ini_logic_new(args)
    args = guess_exchange_and_ust(args)
    schema = await create_conti_eod_schema_name(args['ust'], args['exchange'])
    table = await create_conti_eod_table_name(
        symbol=args['symbol'],
        security_type=args['ust'],
        exchange=args['exchange'],
        contract_number=args['nthcontract']
    )
    limit = 365 * 2
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
    args = eod_ini_logic_new(args)
    args = guess_exchange_and_ust(args)
    schema = await create_conti_eod_schema_name(args['ust'], args['exchange'])
    table = await create_conti_eod_array_table_name(
        symbol=args['symbol'],
        security_type=args['ust'],
        exchange=args['exchange']
    )
    limit = 365 * 2
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


async def nthcontract_to_column_mapping(nthcontract):
    config = {
        1: 'c1',
        2: 'c2',
        3: 'c3',
        4: 'c4',
        5: 'c5',
        6: 'c6',
        7: 'c7',
        8: 'c8',
        9: 'c9',
        10: 'c10',
        11: 'c11',
        12: 'c12'
    }
    return config[int(nthcontract)]


async def select_conti_spread(args):
    args = eod_ini_logic_new(args)
    args = guess_exchange_and_ust(args)
    args['limit'] = 365 * 2
    args['schema'] = await create_conti_eod_schema_name(args['ust'], args['exchange'])
    args['table'] = await create_conti_eod_array_table_name(
        symbol=args['symbol'],
        security_type=args['ust'],
        exchange=args['exchange']
    )
    args['nthcontract1'] = await nthcontract_to_column_mapping(args['nthcontract1'])
    args['nthcontract2'] = await nthcontract_to_column_mapping(args['nthcontract2'])

    return f'''
        SELECT
            dt,
            {args['nthcontract1']} - {args['nthcontract2']} AS value
        FROM {args['schema']}.{args['table']}
        WHERE dt  BETWEEN '{args['startdate']}' AND '{args['enddate']}'
        ORDER BY dt {args['order']}
        LIMIT {args['limit']};
    '''


async def resolve_conti_spread(args, con: Session):
    sql = await select_conti_spread(args)
    data = con.execute(sql).fetchall()
    return data


async def conti_resolver(args, con: Session):
    sql = await eod_continuous_fut_sql_delivery(args)
    data = con.execute(sql).fetchall()
    return data


async def conti_array_resolver(args, db: Session):
    sql = await eod_continuous_fut_array_sql_delivery(args)
    data = db.execute(sql).fetchall()
    return data
