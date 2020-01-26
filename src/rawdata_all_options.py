"""
Route template

"""
from collections import namedtuple
from datetime import datetime as dt
from datetime import date as Date
from datetime import timedelta
import json
import fastapi
from fastapi import Header
from starlette.exceptions import HTTPException
from starlette.status import HTTP_204_NO_CONTENT
from falib.contract import ContractSync
from falib.dayindex import get_day_index_table_name
from falib.dayindex import get_day_index_schema_name
from src.const import OrderChoices
from src.const import tteChoices
from starlette.status import HTTP_400_BAD_REQUEST
from src.utils import guess_exchange_and_ust
from src.utils import eod_ini_logic
from src.utils import CinfoQueries
from src.db import engines
from src.users.auth import bouncer
from src.users.auth import get_current_active_user
from src.users.user_models import UserPy
from starlette.responses import Response
from src.const import time_to_var_func
from enum import Enum


router = fastapi.APIRouter()

from pydantic import BaseModel


class ContentType(str, Enum):
    json: str = 'application/json'
    csv: str = 'application/csv'


@bouncer.roles_required('user')
@router.get(
    '/option-data/single-underlying-single-day',
    summary='Returns all options for one underlying for one (business)day',
    operation_id='get_all_options_single_underlying_single_day'
)
async def get_all_options_single_underlying_single_day(
        symbol: str,
        date: Date,
        ust: str = None,
        exchange: str = None,
        accept: ContentType = Header(default=ContentType.json),
        user: UserPy = fastapi.Depends(get_current_active_user),
):
    """
    A route template. Will set appropriate headers and forward
    the already serialized postgres response.

    - **symbol**: example: 'SPY' or 'spy' (case insensitive)
    - **ust**: underlying security type: 'eqt' e.g.
    - **exchange**: one of: 'usetf', e.g.
    - **date**: format: yyyy-mm-dd
    """
    args = {
        'symbol': symbol,
        'ust': ust,
        'exchange': exchange,
        'date': date
    }
    content = await resolve_options_data(args)
    if accept.value == 'application/json':
        return Response(content=content, media_type='application/json')
    elif accept.value == 'application/csv':
        return Response(content=await to_csv(content), media_type='application/csv')
    else:
        return Response(content=content, media_type='application/json')


async def to_csv(json_str: str) -> str:
    """
    will convert a JSON-string to a CSV-string
    expected schema is [{"key": "value"}]
    where `value` may be `int` or `str`
    """
    data = json.loads(json_str)
    if len(data) == 0:
        return ''
    keys = list(data[0])
    csv = (
            ','.join(keys)
            + '\n'
            + '\n'.join([','.join([str(row[key]) for key in keys]) for row in data])
    )
    return csv


async def get_all_relations(args):
    """
    will query the index table for all table names which
    have a record for a certain business day
    also used in the fitting in local project `py_markets`
    """
    c = ContractSync(
        symbol=args['symbol'],
        security_type=args['ust'],
        exchange=args['exchange']
    )
    schema = get_day_index_schema_name()
    table = get_day_index_table_name(c.compose_3_part_schema_name())
    sql = f'''
        SELECT DISTINCT name 
        FROM {schema}.{table}
        WHERE bizdt = '{args["date"]}';
    '''
    async with engines['options_rawdata'].acquire() as con:
        relations = await con.fetch(sql)
    return relations


async def select_union_all_ltds(args):
    """
    will compose a postgres specific SQL command
    which will return the data as a JSON-string
    """
    args = await guess_exchange_and_ust(args)
    if isinstance(args['date'], Date):
        args['date'] = args['date'].strftime('%Y-%m-%d')
    relations = await get_all_relations(args)
    if len(relations) == 0:
        raise HTTPException(
            status_code=HTTP_204_NO_CONTENT,
            detail=f'not data for selected date `{args["date"]}`'
        )
    c = ContractSync(
        symbol=args['symbol'],
        security_type=args['ust'],
        exchange=args['exchange']
    )
    schema = c.compose_3_part_schema_name()
    sql = 'WITH data AS ('
    for n, record in enumerate(relations):
        sql += f'''(
            SELECT 
                bizdt, undprice, putcall, 
                strkpx, settleprice, volume,
                oi, yte, moneyness,
                divyield, rfr, rawiv,
                delta, tv
            FROM {schema}.{record['name']}
            WHERE bizdt = '{args["date"]}'
        '''
        if n != len(relations) - 1:
            sql += ') UNION ALL '
        else:
            sql += ')'
    sql += '''        )
        SELECT json_agg(data) FROM data;
        '''
    return sql


async def resolve_options_data(args):
    sql = await select_union_all_ltds(args)
    async with engines['options_rawdata'].acquire() as con:
        data = await con.fetch(sql)
        if len(data) != 0:
            return data[0].get('json_agg')
        else:
            return '[]'
