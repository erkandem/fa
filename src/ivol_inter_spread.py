from datetime import date as Date
import typing as t

from falib.contract import ContractSync
import fastapi
from fastapi import Depends
from fastapi.responses import ORJSONResponse
from pydantic import BaseModel
from sqlalchemy.orm.session import Session

from src.const import (
    OrderChoices,
    deltaChoicesPractical,
    time_to_var_func,
    tteChoices,
)
from src.db import get_pgivbase_db
from src.users import (
    User,
    get_current_active_user,
)
from src.utils import (
    eod_ini_logic_new,
    guess_exchange_and_ust,
)

router = fastapi.APIRouter()


class InterSpread(BaseModel):
    dt: Date
    value: t.Union[float, None]


@router.get(
    '/ivol/inter-spread',
    summary='get ivol spread between options with different underlying',
    operation_id='get_ivol_inter_spread',
    response_model=t.List[InterSpread],
    response_class=ORJSONResponse,
)
async def get_ivol_inter_spread(
        symbol1: str,
        symbol2: str,
        ust1: str = None,
        ust2: str = None,
        exchange1: str = None,
        exchange2: str = None,
        tte: tteChoices = tteChoices._1m,
        delta:  deltaChoicesPractical = deltaChoicesPractical._d050,
        startdate: Date = None,
        enddate: Date = None,
        dminus: int = 30,
        order: OrderChoices = OrderChoices._asc,
        con: Session = Depends(get_pgivbase_db),
        user: User = Depends(get_current_active_user),
):
    """
    Calculate the difference between two ETFs or generally the difference between
    two implied volatility series.

    calculation: ``symbol1 - symbol2``
    Response series can include ``null`` where both value are not available.

    - **symbol1**: example: 'SPY' or 'spy' (case insensitive)
    - **ust1**: underlying security type: 'eqt' e.g.
    - **exchange1**: one of: 'usetf', e.g.
    - **symbol2**: example: 'EWZ' or 'ewz' (case insensitive)
    - **ust2**: underlying security type: 'eqt' e.g.
    - **exchange2**: one of: 'usetf', e.g.
    - **tte**: time 'til expiry. 1m 3m 12m ...
    - **delta**: the delta at which to calculate the spread
    - **startdate**: format: yyyy-mm-dd
    - **enddate**: format: yyyy-mm-dd
    - **dminus**: indicate the number of days back from `enddate`
    - **order**:  sorting order with respect to date
    """
    args = {
        'symbol1': symbol1,
        'ust1': ust1,
        'exchange1': exchange1,
        'symbol2': symbol2,
        'ust2': ust2,
        'exchange2': exchange2,
        'tte': tte.value,
        'delta': delta.value,
        'startdate': startdate,
        'enddate': enddate,
        'dminus': dminus,
        'order': order.value,
    }
    content = await resolve_inter_spread(args, con)
    return content


async def select_inter_ivol(args):
    args = eod_ini_logic_new(args)
    args['tte'] = time_to_var_func(args['tte'])
    c_one_args = {
        'symbol': args['symbol1'],
        'exchange': args['exchange1'],
        'ust': args['ust1']
    }
    c_two_args = {
        'symbol': args['symbol2'],
        'exchange': args['exchange2'],
        'ust': args['ust2']
    }

    c_one_args = guess_exchange_and_ust(c_one_args)
    c_two_args = guess_exchange_and_ust(c_two_args)
    c_one = ContractSync()
    c_one.symbol = c_one_args['symbol']
    c_one.exchange = c_one_args['exchange']
    c_one.security_type = c_one_args['ust']
    c_one.target_table_name_base = c_one.compose_ivol_table_name_base()

    c_two = ContractSync()
    c_two.symbol = c_two_args['symbol']
    c_two.exchange = c_two_args['exchange']
    c_two.security_type = c_two_args['ust']
    c_two.target_table_name_base = c_two.compose_ivol_table_name_base()

    schema_one = c_one.compose_2_part_schema_name()
    table_one = c_one.compose_ivol_final_table_name(args['delta'])
    schema_two = c_two.compose_2_part_schema_name()
    table_two = c_two.compose_ivol_final_table_name(args['delta'])

    sql_code = f'''
    WITH data AS (
        SELECT first.dt,
               first.{args['tte']} - second.{args['tte']} AS value
        FROM   {schema_one}.{table_one} first
        FULL OUTER JOIN  {schema_two}.{table_two}  second
            ON first.dt = second.dt
        WHERE first.dt BETWEEN '{args['startdate']}' AND '{args['enddate']}'
        ORDER BY first.dt  {args['order'].upper()}
    )
    SELECT json_agg(data) FROM data;
    '''
    return sql_code


async def resolve_inter_spread(args, con: Session):
    sql = await select_inter_ivol(args)
    data = con.execute(sql).fetchall()
    if len(data) != 0 and len(data[0]) != 0:
        return data[0][0]
    else:
        return []
