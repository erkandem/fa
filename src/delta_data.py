from datetime import datetime as dt
import re
from starlette.responses import Response
import fastapi
import pydantic
from pydantic import BaseModel
from fastapi import Body
from src.db import engines
from src.const import iv_all_sym_choices, exchange_choices
from src.utils import eod_ini_logic_new
from src.users.auth import get_current_active_user
from src.users.user_models import UserPy
from src.rawoption_data import get_schema_and_table_name
from src.const import ust_choices


class DeltaQuery(BaseModel):
    ust: str
    exchange: str
    symbol: str
    option_month: str = None
    underlying_month: str = None
    ltd: str
    startdate: str
    enddate: str

    @pydantic.validator('symbol')
    def symbol_validator(cls, v):
        if v not in iv_all_sym_choices:
            raise ValueError('not a valid value for `symbol`')
        return v

    @pydantic.validator('ust')
    def ust_validator(cls, v):
        if v not in ust_choices:
            raise ValueError('not a valid value for `ust`')
        return v

    @pydantic.validator('exchange')
    def exchange_validator(cls, v):
        if v not in exchange_choices:
            raise ValueError('not a valid value for `exchange`')
        return v

    @pydantic.validator('startdate')
    def startdate_validator(cls, v):
        if len(re.findall(r'^(\d{4}-\d{2}-\d{2})$', v)) == 0:
            raise ValueError('expected format:  yyyy-mm-dd')
        return v

    @pydantic.validator('enddate')
    def enddate_validator(cls, v):
        if len(re.findall(r'^(\d{4}-\d{2}-\d{2})$', v)) == 0:
            raise ValueError('expected format:  yyyy-mm-dd')
        return v

    @pydantic.validator('option_month')
    def option_month_validator(cls, v):
        if len(re.findall(r'^(\d{6})$', v)) == 0:
            raise ValueError('expected format:  yyyymm')
        return v

    @pydantic.validator('underlying_month')
    def underlying_month_validator(cls, v):
        if len(re.findall(r'^(\d{6})$', v)) == 0:
            raise ValueError('expected format:  yyyymm')
        return v


router = fastapi.APIRouter()


@router.post(
    '/delta-contour',
    operation_id='post_delta_data'
)
async def post_delta_data(
        query: DeltaQuery = Body(
            ...,
            example={
                "ust": "fut",
                "exchange": "cme",
                "symbol": "cl",
                "option_month": "201912",
                "underlying_month": "201912",
                "startdate": "2019-01-01",
                "enddate": "2019-04-01",
                "ltd": "20191115"
            }
        ),
        user: UserPy = fastapi.Depends(get_current_active_user)
):
    args = query.dict()
    if 'enddate' in args:
        args['enddate'] = dt.strptime(args['enddate'], '%Y-%m-%d')

    if 'startdate' in args:
        args['startdate'] = dt.strptime(args['startdate'], '%Y-%m-%d')

    data = await resolve_delta_query(args)
    return Response(content=data, media_type='application/json')


async def resolve_delta_query(args: {} = None):
    args = await eod_ini_logic_new(args)
    relation = await get_schema_and_table_name(args)
    if len(relation) != 2:
        return '[]'  # "Could not find particular option chain.", 404
    args['schema'] = relation['schema']
    args['table'] = relation['table']
    sql = delta_query_sql(**args)
    async with engines['options_rawdata'].acquire() as con:
        data = await con.fetch(sql)
        if len(data) != 0:
            return data[0].get('jsonb_object_agg')
        else:
            return '[]'


def delta_query_sql(
        *,
        schema: str,
        table: str,
        startdate: str,
        enddate: str,
        **kwargs
):
    """
    Args:
        schema (str):
        table (str):
        startdate (str):
        enddate (str):

    """
    return f'''
    WITH ex AS (
        SELECT bizdt, strkpx, delta, moneyness, putcall
        FROM {schema}.{table}
    -------------- (select the last LIMIT days  -------------
        WHERE bizdt BETWEEN '{startdate}' AND '{enddate}'
        ORDER BY bizdt, strkpx DESC 
    ), smry AS (
        ---------- apply different filtering with -----------
        ---------- respect to delta and moneyness -----------
        ---------- depending on put or call -----------------
        (    
            SELECT   bizdt, putcall, strkpx, delta + 1 as delta, moneyness
            FROM ex
            WHERE bizdt  IN (SELECT DISTINCT bizdt FROM ex ORDER BY bizdt DESC)
                AND moneyness >= 0
                AND putcall = 0
            ORDER BY strkpx DESC 
        ) UNION ALL (
            SELECT bizdt, putcall, strkpx, delta, moneyness
            FROM ex
            WHERE bizdt IN (SELECT DISTINCT bizdt FROM ex ORDER BY bizdt DESC)
                AND moneyness < 0
                AND putcall = 1
            ORDER BY strkpx DESC
        ) 
    ), resp AS (
        ---------------- first JSON wrapper --------------------------
        SELECT bizdt, jsonb_object_agg(strkpx, delta) AS delta
        FROM smry
        --------------- replace missing values with 'null' -----------
        RIGHT JOIN (
            (SELECT DISTINCT bizdt FROM smry) a
            CROSS JOIN
            (SELECT DISTINCT strkpx FROM smry ORDER BY strkpx) b
           ) c
           USING      (bizdt, strkpx)
           GROUP BY   bizdt
           ORDER BY   bizdt DESC
    )
    --------------- final select and JSON wrapper -------------------
    SELECT jsonb_object_agg(bizdt, delta) FROM resp; 
    --------------------- and we are done ---------------------------
    '''
