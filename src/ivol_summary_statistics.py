
"""
Route template

"""
from collections import namedtuple
from datetime import datetime as dt
from datetime import date as Date
from datetime import timedelta
from typing import List
import fastapi
from starlette.status import HTTP_400_BAD_REQUEST
from starlette.responses import Response
from falib.contract import ContractSync
from src.const import OrderChoices
from src.const import tteChoices
from src.const import time_to_var_func
from src.const import deltaChoicesPractical
from src.db import engines
from src.users.auth import bouncer
from src.users.auth import get_current_active_user
from src.users.user_models import UserPy
from src.utils import CinfoQueries
from src.utils import eod_ini_logic
from src.utils import eod_ini_logic_new
from src.utils import guess_exchange_and_ust
from pydantic import BaseModel


class VolaSummary(BaseModel):
    symbol: str
    start_date: str
    end_date: str
    delta: str
    expiry: str
    standard_dev: float
    average: float
    min: float
    max: float
    observations: float
    last: float
    week_ago_one: float
    week_ago_two: float
    week_ago_three: float
    week_ago_four: float
    week_ago_five: float
    week_ago_six: float


router = fastapi.APIRouter()


@bouncer.roles_required('user')
@router.get(
    '/ivol/summary/single',
    summary='get min, max, std, average and weekly data points',
    operation_id='get_ivol_summary_single',
    response_model=VolaSummary
)
async def get_ivol_summary_single(
        symbol: str,
        ust: str = None,
        exchange: str = None,
        tte: tteChoices = tteChoices._1m,
        startdate: Date = None,
        enddate: Date = None,
        dminus: int = 365,
        delta: deltaChoicesPractical = deltaChoicesPractical._d050,
        user: UserPy = fastapi.Depends(get_current_active_user)
):
    """
    Returns descriptive statistics and some slices of implied volatility data
    last, 1 week, 2 week, 3 week, 4 week, 5 week and 6 week ago

    - **symbol**: example: 'SPY' or 'spy' (case insensitive)
    - **ust**: underlying security type: 'eqt' e.g.
    - **exchange**: one of: 'usetf', e.g.
    - **startdate**: format: yyyy-mm-dd
    - **enddate**: format: yyyy-mm-dd
    - **dminus**: indicate the number of days back from `enddate`
    - **tte**: time 'til expiry: 1m 3m 12m ...
    - **delta**: a single delta. d050 by default.
    """
    args = {
        'symbol': symbol,
        'ust': ust,
        'exchange': exchange,
        'tte': tte._value_,
        'startdate': startdate,
        'enddate': enddate,
        'dminus': dminus,
        'delta': delta.value
    }
    content = await resolve_ivol_summary_statistics(args)
    return content


@bouncer.roles_required('user')
@router.get(
    '/ivol/summary/cme',
    summary='get min, max, std, average and weekly data points for symbols on CME',
    operation_id='get_ivol_summary_cme'
)
async def get_ivol_summary_cme(
        user: UserPy = fastapi.Depends(get_current_active_user)
):
    """
    Returns descriptive statistics and some slices of data for for selected symbols traded at CME

    """
    args = {
        'ust': 'fut',
        'exchange': 'cme',
        'tte': tteChoices._1m.value,
        'startdate': None,
        'enddate': None,
        'dminus': 365,
        'delta': deltaChoicesPractical._d050.value
    }
    content = await resolve_ivol_summary_multi(args)
    return content


@bouncer.roles_required('user')
@router.get(
    '/ivol/summary/ice',
    summary='get min, max, std, average and weekly data points for sybmols on ICE',
    operation_id='get_ivol_summary_ice',
    response_model=List[VolaSummary]
)
async def get_ivol_summary_ice(
        user: UserPy = fastapi.Depends(get_current_active_user)
):
    """
    Returns descriptive statistics and some slices of data for symbols traded at ICE
    """
    args = {
        'ust': 'fut',
        'exchange': 'ice',
        'tte': tteChoices._1m.value,
        'startdate': None,
        'enddate': None,
        'dminus': 365,
        'delta': deltaChoicesPractical._d050.value
    }
    content = await resolve_ivol_summary_multi(args)
    return content


@bouncer.roles_required('user')
@router.get(
    '/ivol/summary/usetf',
    summary='get min, max, std, average and weekly data points for US ETFs',
    operation_id='get_ivol_summary_usetf',
    response_model=List[VolaSummary]
)
async def get_ivol_summary_usetf(
        user: UserPy = fastapi.Depends(get_current_active_user)
):
    """
    Returns descriptive statistics and some slices of data for selected US ETFs
    """
    args = {
        'ust': 'eqt',
        'exchange': 'usetf',
        'tte': tteChoices._1m.value,
        'startdate': None,
        'enddate': None,
        'dminus': 365,
        'delta': deltaChoicesPractical._d050.value
    }
    content = await resolve_ivol_summary_multi(args)
    return content


@bouncer.roles_required('user')
@router.get(
    '/ivol/summary/eurex',
    summary='get min, max, std, average and weekly data points for symbols on EUREX',
    operation_id='get_ivol_summary_eurex',
    response_model=List[VolaSummary]
)
async def get_ivol_summary_eurex(
        user: UserPy = fastapi.Depends(get_current_active_user)
):
    """
    Returns descriptive statistics and some slices of data for selected symbols traded at EUREX
    """
    args_futures = {
        'ust': 'fut',
        'exchange': 'eurex',
        'tte': tteChoices._1m.value,
        'startdate': None,
        'enddate': None,
        'dminus': 365,
        'delta': deltaChoicesPractical._d050.value
    }
    args_indices = {
        'ust': 'ind',
        'exchange': 'eurex',
        'tte': tteChoices._1m.value,
        'startdate': None,
        'enddate': None,
        'dminus': 365,
        'delta': deltaChoicesPractical._d050.value
    }
    content = await resolve_ivol_summary_multi(args_indices)
    content += await resolve_ivol_summary_multi(args_futures)
    return content


async def select_statistics_single(args):
    """ """
    six_weeks = 5 * 6 + 1
    if args['dminus'] < six_weeks:
        args['dminus'] = str(six_weeks)
    args = await eod_ini_logic_new(args)
    args = await guess_exchange_and_ust(args)
    tte_human_readable = args['tte']
    args['tte'] = time_to_var_func(args['tte'])

    c = ContractSync()
    c.symbol = args['symbol']
    c.exchange = args['exchange']
    c.security_type = args['ust']
    c.target_table_name_base = c.compose_ivol_table_name_base()

    schema = c.compose_2_part_schema_name()
    table = c.compose_ivol_final_table_name(args['delta'])
    return f'''   SELECT 
               '{args['symbol']}'                                 AS symbol,
               (ARRAY_AGG(dt ORDER BY dt ASC))[1]::date           AS start_date,
               (ARRAY_AGG(dt ORDER BY dt DESC))[1]::date          AS end_date,
               '{args['delta']}'                                  AS delta,
               '{tte_human_readable}'                             AS expiry,
               STDDEV_SAMP({args['tte']})                         AS standard_dev,
               AVG({args['tte']})                                 AS average,
               MIN({args['tte']})                                 AS min,
               MAX({args['tte']})                                 AS max,
               COUNT(dt)                                          AS observations,
               (array_agg({args['tte']} ORDER BY dt DESC))[1]     AS last,
               (array_agg({args['tte']} ORDER BY dt DESC))[5*1+1] AS week_ago_one,
               (array_agg({args['tte']} ORDER BY dt DESC))[5*2+1] AS week_ago_two,
               (array_agg({args['tte']} ORDER BY dt DESC))[5*3+1] AS week_ago_three,
               (array_agg({args['tte']} ORDER BY dt DESC))[5*4+1] AS week_ago_four,
               (array_agg({args['tte']} ORDER BY dt DESC))[5*5+1] AS week_ago_five,
               (array_agg({args['tte']} ORDER BY dt DESC))[5*6+1] AS week_ago_six
    FROM       {schema}.{table}
    WHERE      dt
    BETWEEN    '{args['startdate']}' AND '{args['enddate']}';'''


async def select_ivol_summary_multi(args):
    sql_info = CinfoQueries.symbol_where_ust_and_exchange_f(args)
    async with engines['options_rawdata'].acquire() as con:
        symbols = await con.fetch(sql_info)
    sql_code = '( '
    symbols_length = len(symbols)
    for n, symbol in enumerate(symbols):
        individual_args = {
            'symbol': symbol[0],
            'ust': args['ust'],
            'exchange': args['exchange'],
            'tte': args['tte'],
            'startdate': args['startdate'],
            'enddate': args['enddate'],
            'dminus': args['dminus'],
            'delta': args['delta']
        }
        sql_code += (await select_statistics_single(individual_args))[0:-1]
        if n < symbols_length - 1:
            sql_code += '\n)\n   UNION ALL\n(\n '
    sql_code += ');'
    return sql_code


async def resolve_ivol_summary_multi(args):
    sql = await select_ivol_summary_multi(args)
    async with engines['pgivbase'].acquire() as con:
        data = await con.fetch(sql)
        return data


async def resolve_ivol_summary_statistics(args):
    sql = await select_statistics_single(args)
    async with engines['pgivbase'].acquire() as con:
        data = await con.fetch(sql)
        if len(data) != 0:
            return dict(data[0])
        else:
            return [{}]
