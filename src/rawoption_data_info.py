import fastapi
import pydantic
from fastapi import Depends, Body
from pydantic import BaseModel, Schema
from src.db import engines
from src.const import ust_choices, pc_choices
from src.const import RAWOPTION_MAP
from src.users.user_models import UserPy
from src.users.auth import get_current_active_user
from src.const import RawDataMetricChoices, PutCallChoices, OrderChoices
from src.utils import CinfoQueries
from src.db import engines
from datetime import date as Date
from typing import Union, List
from fastapi import Query
from src.rawoption_data import get_schema_and_table_name


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
            raise ValueError(f'allowd: {pc_choices}, recieved: {v}')
        return v


router = fastapi.APIRouter()


@router.get(
    '/usts',
    operation_id='get_api_info_usts'
)
async def get_api_info_usts(
        user: UserPy = Depends(get_current_active_user)
):
    """return available ``ust``"""
    args = {}
    sql = CinfoQueries.ust_f(args)
    async with engines['yh'].acquire() as con:
        res = await con.fetch(sql)
        return res


@router.get(
    '/exchanges',
    operation_id='get_api_info_exchanges'
)
async def get_api_info_exchanges(
        ust: str,
        user: UserPy = Depends(get_current_active_user)
):
    """return available ``exchange`` for a given ``ust``"""
    args = {'ust': ust}
    if args['ust']:
        sql = CinfoQueries.exchange_where_ust_f(args)
    else:
        sql = CinfoQueries.exchange_f(args)
    async with engines['yh'].acquire() as con:
        res = await con.fetch(sql)
        return res


@router.get(
    '/symbols',
    operation_id='get_api_info_symbols'
)
async def get_api_info_symbols(
        ust: str,
        exchange: str,
        user: UserPy = Depends(get_current_active_user)
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
    async with engines['yh'].acquire() as con:
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
        user: UserPy = Depends(get_current_active_user)
):
    """return ``ltd`` given ``ust``, ``exchange``, ``symbol``"""
    args = {'ust': ust, 'exchange': exchange, 'symbol': symbol}
    sql = CinfoQueries.ltd_where_ust_exchange_and_symbol_f(args)
    async with engines['yh'].acquire() as con:
        res = await con.fetch(sql)
        return res


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
    )
):
    """ same as `GET` route, but containing the query within the body"""
    args = data.dict()
    result = await resolve_strikes(args)
    return result


async def resolve_strikes(args: {}):
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
    async with engines['yh'].acquire() as con:
        data = await con.fetch(sql)
        return data
