"""
Route template

"""
from datetime import date as Date
import fastapi
from fastapi import Depends
from sqlalchemy.engine import Connection

from falib.contract import ContractSync
from src.const import OrderChoices
from src.const import tteChoices
from src.db import get_pgivbase_db
from src.const import time_to_var_func
from src.const import deltaChoicesPractical
import typing as t
from pydantic import BaseModel
from src.utils import guess_exchange_and_ust
from src.utils import eod_ini_logic_new
from sqlalchemy.engine import Connection
from src.db import get_pgivbase_db
from fastapi import Depends

router = fastapi.APIRouter()

class ivol_calendar(BaseModel):
    dt: Date
    value: float

@router.get(
    '/ivol/calendar',
    summary='Calculate the spread between different expiries',
    operation_id='get_ivol_calendar',
    response_model=t.List[ivol_calendar],
)
async def get_ivol_calendar(
        symbol: str,
        ust: str = None,
        exchange: str = None,
        startdate: Date = None,
        enddate: Date = None,
        dminus: int = 30,
        tte1: tteChoices = tteChoices._1m,
        tte2: tteChoices = tteChoices._2m,
        delta1: deltaChoicesPractical = deltaChoicesPractical._d050,
        delta2: deltaChoicesPractical = deltaChoicesPractical._d050,
        order: OrderChoices = OrderChoices._asc,
        con: Connection = Depends(get_pgivbase_db),
):
    """

    A calendar spread is the difference of implied volatility between
    two different expiry dates and optionally different deltas.


    - **symbol**: example: 'SPY' or 'spy' e.g., case insensitive
    - **ust**: underlying security type: 'eqt' e.g.
    - **exchange**: one of: 'usetf' e.g.
    - **tte**: time until expiry: '1m', '2m', '3m' e.g.
    - **startdate**: format: yyyy-mm-dd
    - **enddate**: format: yyyy-mm-dd
    - **dminus**: indicate the number of days back from `enddate`
    - **tt1**: time 'til expiry of first leg
    - **tt2**: time 'til expiry of second leg
    - **delta1**: manually set the first delta leg
    - **delta2**: manually set the second delta leg
    - **order**:  sorting order with respect to date
    """
    if delta1:
        delta1 = delta1.value
    if delta2:
        delta2 = delta2.value

    args = {
        'symbol': symbol,
        'ust': ust,
        'exchange': exchange,
        'startdate': startdate,
        'enddate': enddate,
        'dminus': dminus,
        'tte1': tte1._value_,
        'tte2': tte2._value_,
        'delta1': delta1,
        'delta2': delta2,
        'order': order.value
    }
    content = await resolve_ivol_calendar_spread(args, con)
    return content


async def select_calendar_spread(args):
    args = eod_ini_logic_new(args)
    args = guess_exchange_and_ust(args)
    args['tte1'] = time_to_var_func(args['tte1'])
    args['tte2'] = time_to_var_func(args['tte2'])

    c = ContractSync()
    c.symbol = args['symbol']
    c.exchange = args['exchange']
    c.security_type = args['ust']
    c.target_table_name_base = c.compose_ivol_table_name_base()

    schema = c.compose_2_part_schema_name()
    table_first = c.compose_ivol_final_table_name(args['delta1'])
    table_second = c.compose_ivol_final_table_name(args['delta2'])

    sql = f'''
    WITH data AS (
        SELECT 
            first.dt as dt,
            first.{args['tte1']} - second.{args['tte2']} AS value
        FROM {schema}.{table_first} first
        FULL OUTER JOIN  {schema}.{table_second} second
            ON first.dt = second.dt
        WHERE first.dt  BETWEEN '{args['startdate']}' AND '{args['enddate']}'
        ORDER BY dt {args['order'].upper()}
    )
    SELECT json_agg(data) as json_agg FROM data;
    '''
    return sql


async def resolve_ivol_calendar_spread(args, con: Connection):
    sql = await select_calendar_spread(args)
    data = con.execute(sql).fetchall()
    if len(data) > 0 and len(data[0]) > 0:
        return data[0][0]
    else:
        return []
