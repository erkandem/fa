import json
from collections import namedtuple
from datetime import datetime as dt
from datetime import date as Date
from datetime import timedelta
import fastapi
from pydantic import BaseModel
from falib.contract import Contract
from src.const import time_to_var_func
from src.const import OrderChoices
from src.const import tteChoices
from src.utils import guess_exchange_and_ust
from src.utils import eod_ini_logic
from src.db import engines
from src.const import iv_all_sym_choices
from src.const import ust_choices
from src.const import delta_choices_practical
from src.const import exchange_choices
from src.const import time_to_var_func
from src.const import delta_choices
from typing import List
from src.users.auth import bouncer
from src.users.auth import get_current_active_user
from src.users.user_models import UserPy
from starlette.responses import Response


router = fastapi.APIRouter()


class SurfaceValue(BaseModel):
    var1: float
    var2: float
    var3: float
    var4: float
    var5: float
    var6: float
    var8: float
    var9: float
    var10: float
    var11: float
    var12: float
    var13: float
    var14: float
    var15: float
    var16: float


class SurfaceAggregate(BaseModel):
        dt: Date
        delta: str
        values: SurfaceValue


@bouncer.roles_required('user')
@router.get(
    '/ivol/surface',
    response_model=List[SurfaceAggregate],
    operation_id='get_surface_by_delta',
    summary='returns a surface parameterized by delta and constant time'
)
async def get_surface_by_delta(
        symbol: str,
        date: Date = None,
        exchange: str = None,
        ust: str = None,
        user: UserPy = fastapi.Depends(get_current_active_user)
):
    """
    - **symbol**: example: 'SPY' or 'spy' (case insensitive)
    - **ust**: underlying security type: ['fut', 'eqt', 'ind', 'fx']
    - **exchange**: one of: ['usetf', 'cme', 'ice', 'eurex']
    - **date**' date of implied volatility surface to be returned
    """
    args = {'date': date, 'symbol': symbol, 'exchange': exchange, 'ust': ust}
    content = await surface_resolver(args)
    return Response(content=content, media_type='application/json')


async def prepare_surface_sql_arguments(args):
    """Deprecated in favor of JSON delivery via ``surface_json``"""
    args = await guess_exchange_and_ust(args)
    args['date'] = dt.strptime(args['date'], '%Y-%m-%d').strftime('%Y-%m-%d')
    c = Contract()
    c.symbol = args['symbol']
    c.exchange = args['exchange']
    c.security_type = args['ust']
    c.target_table_name_base = await c.compose_ivol_table_name_base()
    schema = await c.compose_2_part_schema_name()
    vars = ', '.join([f'var{n}' for n in range(1, 16 + 1, 1)])
    union = ' UNION ALL '
    sql_code = ''
    for k, strip in enumerate(delta_choices_practical):
        if k == len(delta_choices_practical) - 1:
            union = ';'
        table = await c.compose_ivol_final_table_name(strip)
        sql_code += f'''
        (SELECT       dt AS dt,
                      '{strip}' AS delta,
                      {vars}
         FROM         {schema}.{table}
         WHERE        dt = '{args['date']}'){union}'''
    return sql_code


async def resolve_last_date(c: Contract) -> str:
    schema = await c.compose_2_part_schema_name()
    table = await c.compose_ivol_final_table_name('d050')
    sql = f'SELECT max(dt) FROM {schema}.{table};'
    async with engines['pgivbase'].acquire() as con:
        data = await con.fetch(query=sql)
    return data[0][0].strftime('%Y-%m-%d')


async def surface_json(args):
    """ """
    args = await guess_exchange_and_ust(args)
    c = Contract()
    c.symbol = args['symbol']
    c.exchange = args['exchange']
    c.security_type = args['ust']
    c.target_table_name_base = await c.compose_ivol_table_name_base()
    if args['date'] is None:
        args['date'] = await resolve_last_date(c)
    else:
        args['date'] = args['date'].strftime('%Y-%m-%d')
    schema = await c.compose_2_part_schema_name()
    vars = ', '.join([f'var{n}' for n in range(1, 16 + 1, 1)])
    union = ' UNION ALL '
    sql_code = ''
    for k, strip in enumerate(delta_choices_practical):
        if k == len(delta_choices_practical) - 1:
            union = ''
        table = await c.compose_ivol_final_table_name(strip)
        sql_code += f'''
                (
                    SELECT     dt as dt,
                               '{strip}' as delta,
                               (SELECT row_to_json(t)
                               FROM (
                                   SELECT {vars}
                                   FROM {schema}.{table}
                                   WHERE dt = '{args['date']}'
                                   ) t
                               ) AS values
                    FROM {schema}.{table}
                    WHERE dt = '{args['date']}'
                ) {union}'''

    sql_code = f'''
    WITH level_one AS (
        {sql_code}
    )
    SELECT json_agg(level_one) as surface_ts
    FROM level_one;
    '''
    return sql_code


async def surface_resolver(args: dict):
    sql = await surface_json(args)
    async with engines['pgivbase'].acquire() as con:
        data = await con.fetch(sql)
        if len(data) != 0:
            return data[0].get('surface_ts')
        else:
            return '[]'
