import fastapi
import pydantic
from fastapi import Depends, Body, Query
from src.const import pc_choices
from src.const import PutCallChoices
from src.users import get_current_active_user, User
from src.utils import CinfoQueries

from datetime import date as Date
from typing import Union
from src.rawoption_data import get_schema_and_table_name
from src.db import get_options_rawdata_db, results_proxy_to_list_of_dict
import typing as t
from pydantic import BaseModel
from sqlalchemy.orm.session import Session


class FirstAndLast(BaseModel):
    first_date: Date
    last_date: Date


class Bulk(BaseModel):
    value: Union[str, Date, float, int]


class GetStrikesModel(BaseModel):
    """TODO: validate params"""

    ust: str
    exchange: str
    symbol: str
    putcall: PutCallChoices
    ltd: str

    @pydantic.validator('putcall')
    def putcall_validator(cls, v):
        if v not in pc_choices:
            raise ValueError(f'allowed: {pc_choices}, received: {v}')
        return v


router = fastapi.APIRouter()


class Ust(BaseModel):
    ust: str

@router.get(
    '/usts',
    operation_id='get_api_info_usts',
    response_model=t.List[Ust],
)
async def get_api_info_usts(
    con: Session = Depends(get_options_rawdata_db),
    user: User = Depends(get_current_active_user),
):
    """return available ``ust``s"""
    args = {}
    sql = CinfoQueries.ust_f(args)
    res = con.execute(sql).fetchall()
    return res


class Exchange(BaseModel):
    exchange: str

@router.get(
    '/exchanges',
    operation_id='get_api_info_exchanges',
    response_model=t.List[Exchange],
)
async def get_api_info_exchanges(
        ust: str,
        con: Session = Depends(get_options_rawdata_db),
        user: User = Depends(get_current_active_user),
):
    """return available ``exchange`` for a given ``ust``"""
    args = {
        'ust': ust,
    }
    if args['ust']:
        sql = CinfoQueries.exchange_where_ust_f(args)
    else:
        sql = CinfoQueries.exchange_f(args)
    res = con.execute(sql).fetchall()
    return res


class Symbol(BaseModel):
    symbol: str


@router.get(
    '/symbols',
    operation_id='get_api_info_symbols',
    response_model=t.List[Symbol],
)
async def get_api_info_symbols(
        ust: str,
        exchange: str,
        con: Session = Depends(get_options_rawdata_db),
        user: User = Depends(get_current_active_user),
):
    """
    TODO: validate ``ust`` and ``exchange``
    return symbols for ``ust`` and/or ``exchange``
    """
    args = {
        'ust': ust,
        'exchange': exchange,
    }
    if args['ust']:
        ust_exists = 1100
    else:
        ust_exists = 1000
    if args['exchange']:
        exchange_exists = 11
    else:
        exchange_exists = 10
    hash = exchange_exists + ust_exists
    if hash == 1111:
        sql = CinfoQueries.symbol_where_ust_and_exchange_f(args)
    elif hash == 1110:
        sql = CinfoQueries.symbol_where_ust_f(args)
    elif hash == 1011:
        sql = CinfoQueries.symbol_where_exchange_f(args)
    else:
        sql = CinfoQueries.symbol_f(args)
    res = con.execute(sql).fetchall()
    return res


class Ltd(BaseModel):
    ltd: str


@router.get(
    '/last-trading-days',
    operation_id='get_api_info_ltd',
    response_model=t.List[Ltd],
)
async def get_api_info_ltd(
        ust: str,
        exchange: str,
        symbol: str,
        con: Session = Depends(get_options_rawdata_db),
        user: User = Depends(get_current_active_user),
):
    """
    return the available last trading days (`ltd`).
    (i.e. available option chains)

    [{'ltd': '20241115'}, {'ltd': '20251117'}, ...]

    """
    args = {
        'ust': ust,
        'exchange': exchange,
        'symbol': symbol,
    }
    sql = CinfoQueries.ltd_where_ust_exchange_and_symbol_f(args)
    cursor = con.execute(sql)
    data = results_proxy_to_list_of_dict(cursor)
    return data


class OptionMonthAndUnderlyingMonth(BaseModel):
    option_month: str
    underlying_month: str


@router.get(
    '/option-month-and-underlying-month',
    operation_id='get_api_info_option_month_and_underlying_month',
    response_model=t.List[OptionMonthAndUnderlyingMonth]
)
async def get_api_info_option_month_and_underlying_month(
        ust: str,
        exchange: str,
        symbol: str,
        ltd: str,
        con: Session = Depends(get_options_rawdata_db),
        user: User = Depends(get_current_active_user),
):
    """
    return the `option_month` and `underlying_month` for an option chain.
    Relevant for options on futures.
    """
    query = {
        'ust': ust,
        'exchange': exchange,
        'symbol': symbol,
        'ltd': ltd,
    }
    sql = CinfoQueries.option_month_underlying_month_f(query)
    cursor = con.execute(sql)
    data = results_proxy_to_list_of_dict(cursor)
    return data


class FirstLast(BaseModel):
    first: Date
    last: Date


@router.get(
    '/first-and-last',
    operation_id='get_api_info_first_and_last',
    response_model=t.List[FirstLast],
)
async def get_api_info_first_and_last(
        ust: str,
        exchange: str,
        symbol: str,
        ltd: str,
        option_month: str = None,
        underlying_month: str = None,
        con: Session = Depends(get_options_rawdata_db),
        user: User = Depends(get_current_active_user),
):
    """
    return the first and last date of a option series data set
    """
    args = {
        'ust': ust,
        'exchange': exchange,
        'symbol': symbol,
        'ltd': ltd,
        'option_month': option_month,
        'underlying_month': underlying_month,
    }
    meta = await get_schema_and_table_name(args, con)
    if len(meta) != 2:
        return []
    args['schema'] = meta['schema']
    args['table'] = meta['table']
    sql = CinfoQueries.first_and_last_f(args)
    cursor = con.execute(sql)
    data = results_proxy_to_list_of_dict(cursor)
    return data


class Strike(BaseModel):
    strike: float


@router.get(
    '/strikes',
    operation_id='get_api_info_strikes',
    response_model=t.List[Strike],
)
async def get_api_info_strikes(
        ust: str,
        exchange: str,
        symbol: str,
        putcall: str,
        ltd: str,
        con: Session = Depends(get_options_rawdata_db),
        user: User = Depends(get_current_active_user),
):
    """
    TODO: Validate parameters
    return the strikes available for an options chain
    """
    args = {
        'ust': ust,
        'exchange': exchange,
        'symbol': symbol,
        'putcall': putcall,
        'ltd': ltd,
    }
    result = await resolve_strikes(args, con)
    return result


@router.post(
    '/strikes',
    operation_id='post_api_info_strikes',
    response_model=t.List[Strike],
)
async def post_api_info_strikes(
        data: GetStrikesModel = Body(
            ...,
            example={
                "ust": "eqt",
                "exchange": "usetf",
                "symbol": "xop",
                "putcall": "call",
                "ltd": "20200117"
            }
        ),
        con: Session = Depends(get_options_rawdata_db),
        user: User = Depends(get_current_active_user),
):
    """
    return the strikes available for an options chain

    same as `GET` route, but containing the query within the body
    """
    args = data.dict()
    result = await resolve_strikes(args, con)
    return result


async def resolve_strikes(args: t.Dict, con: Session):
    relation = await get_schema_and_table_name(args, con)
    if len(relation) != 2:
        return []
    args2 = {}
    if args['putcall'] == 'put':
        args2['putcall'] = 0
    elif args['putcall'] == 'call':
        args2['putcall'] = 1
    args2['schema'] = relation['schema']
    args2['table'] = relation['table']
    sql = CinfoQueries.strikes_where_table_and_pc_f(args2)
    cursor = con.execute(sql)
    data = results_proxy_to_list_of_dict(cursor)
    return data
