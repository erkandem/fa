from datetime import date as Date
from datetime import datetime as dt
import typing as t

from falib.contract import Contract
import fastapi
from fastapi import Depends
from fastapi.responses import ORJSONResponse
from pydantic import BaseModel
from sqlalchemy.orm.session import Session

from src.const import delta_choices_practical
from src.db import get_pgivbase_db
from src.users import (
    User,
    get_current_active_user,
)
from src.utils import guess_exchange_and_ust

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


@router.get(
    '/ivol/surface',
    operation_id='get_surface_by_delta',
    summary='returns a surface parameterized by delta and constant time',
    response_model=t.List[SurfaceAggregate],
    response_class=ORJSONResponse,
)
async def get_surface_by_delta(
        symbol: str,
        date: Date = None,
        exchange: str = None,
        ust: str = None,
        con: Session = Depends(get_pgivbase_db),
        user: User = Depends(get_current_active_user),
):
    """
    - **symbol**: example: 'SPY' or 'spy' (case insensitive)
    - **ust**: underlying security type: ['fut', 'eqt', 'ind', 'fx']
    - **exchange**: one of: ['usetf', 'cme', 'ice', 'eurex']
    - **date**' date of implied volatility surface to be returned
    """
    args = {
        'date': date,
        'symbol': symbol,
        'exchange': exchange,
        'ust': ust,
    }
    content = await surface_resolver(args, con)
    return content


async def prepare_surface_sql_arguments(args):
    """Deprecated in favor of JSON delivery via ``surface_json``"""
    args = guess_exchange_and_ust(args)
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


async def resolve_last_date(c: Contract, con: Session) -> str:
    schema = await c.compose_2_part_schema_name()
    table = await c.compose_ivol_final_table_name('d050')
    sql = f'SELECT max(dt) FROM {schema}.{table};'
    data = con.execute(sql).fetchall()
    return data[0][0].strftime('%Y-%m-%d')


async def surface_json(args, con):
    """ """
    args = guess_exchange_and_ust(args)
    c = Contract()
    c.symbol = args['symbol']
    c.exchange = args['exchange']
    c.security_type = args['ust']
    c.target_table_name_base = await c.compose_ivol_table_name_base()
    if args['date'] is None:
        args['date'] = await resolve_last_date(c, con)
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


async def surface_resolver(
        args: t.Dict[str, t.Any],
        con: Session,
):
    sql = await surface_json(args, con)
    data = con.execute(sql).fetchall()
    if len(data) != 0 and len(data[0]) != 0:
        return data[0][0]
    else:
        return []
