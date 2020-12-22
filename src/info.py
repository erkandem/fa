import fastapi
import pydantic
from fastapi import Depends, Body
from pydantic import BaseModel
from src.const import pc_choices
from src.users.models import UserPy
from src.const import PutCallChoices
from src.utils import CinfoQueries
from appconfig import engines
from datetime import date as Date
from typing import Union
from src.rawoption_data import get_schema_and_table_name
from asyncpg.pool import Pool


class FirstAndLast(BaseModel):
    first_date: Date
    last_date: Date


class Bulk(BaseModel):
    value: Union[str, Date, float, int]


class GetStrikesModel(BaseModel):
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


@router.get(
    '/usts',
    operation_id='get_api_info_usts'
)
async def get_api_info_usts(
):
    """return available ``ust``"""
    args = {}
    sql = CinfoQueries.ust_f(args)
    async with engines.options_rawdata.acquire() as con:
        res = await con.fetch(sql)
        return res


@router.get(
    '/exchanges',
    operation_id='get_api_info_exchanges'
)
async def get_api_info_exchanges(
        ust: str,
):
    """return available ``exchange`` for a given ``ust``"""
    args = {'ust': ust}
    if args['ust']:
        sql = CinfoQueries.exchange_where_ust_f(args)
    else:
        sql = CinfoQueries.exchange_f(args)
    async with engines.options_rawdata.acquire() as con:
        res = await con.fetch(sql)
        return res


@router.get(
    '/symbols',
    operation_id='get_api_info_symbols'
)
async def get_api_info_symbols(
        ust: str,
        exchange: str,
):
    """return symbols according to ``ust`` and/or ``exchange``"""
    args = {'ust': ust, 'exchange': exchange}
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
    async with engines.options_rawdata.acquire() as con:
        res = await con.fetch(sql)
        return res


@router.get(
    '/last-trading-days',
    operation_id='get_api_info_ltd'
)
async def get_api_info_ltd(
        ust: str,
        exchange: str,
        symbol: str,
):
    """return ``ltd`` given ``ust``, ``exchange``, ``symbol``"""
    args = {
        'ust': ust,
        'exchange': exchange,
        'symbol': symbol,
    }
    sql = CinfoQueries.ltd_where_ust_exchange_and_symbol_f(args)
    async with engines.options_rawdata.acquire() as con:
        res = await con.fetch(sql)
        return res


@router.get(
    '/option-month-and-underlying-month',
    operation_id='get_api_info_option_month_and_underlying_month'
)
async def get_api_info_option_month_and_underlying_month(
        ust: str,
        exchange: str,
        symbol: str,
        ltd: str,

):
    query = {
        'ust': ust,
        'exchange': exchange,
        'symbol': symbol,
        'ltd': ltd
    }
    sql = CinfoQueries.option_month_underlying_month_f(query)
    async with engines.options_rawdata.acquire() as con:
        data = await con.fetch(sql)
        return data


@router.get(
    '/first-and-last',
    operation_id='get_api_info_first_and_last'
)
async def get_api_info_first_and_last(
        ust: str,
        exchange: str,
        symbol: str,
        ltd: str,
        option_month: str = None,
        underlying_month: str = None,
):
    args = {
        'ust': ust,
        'exchange': exchange,
        'symbol': symbol,
        'ltd': ltd,
        'option_month': option_month,
        'underlying_month': underlying_month,
    }
    meta = await get_schema_and_table_name(args)
    if len(meta) == 0:
        return []
    args['schema'] = meta['schema']
    args['table'] = meta['table']
    sql = CinfoQueries.first_and_last_f(args)
    async with engines.options_rawdata.acquire() as con:
        data = await con.fetch(sql)
        return data


@router.post(
    '/strikes',
    operation_id='post_api_info_strikes'
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
):
    """ same as `GET` route, but containing the query within the body"""
    args = data.dict()
    result = await resolve_strikes(args, pool=engines.options_rawdata)
    return result


async def resolve_strikes(args: {}, pool: Pool):
    relation = await get_schema_and_table_name(args)
    if len(relation) == 0:
        return []
    args2 = {}
    if args['putcall'] == 'put':
        args2['putcall'] = 0
    elif args['putcall'] == 'call':
        args2['putcall'] = 1
    args2['schema'] = relation[0]['schema_name']
    args2['table'] = relation[0]['table_name']
    sql = CinfoQueries.strikes_where_table_and_pc_f(args2)
    async with pool.acquire() as con:
        data = await con.fetch(sql)
        return data
