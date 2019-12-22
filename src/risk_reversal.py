"""
Route template

"""
from collections import namedtuple
from datetime import datetime as dt
from datetime import date
from datetime import timedelta
import fastapi
from falib.contract import ContractSync
from src.const import time_to_var_func
from src.const import OrderChoices
from src.const import tteChoices
from src.const import deltaChoicesPractical
from src.const import deltaOffsetChoices
from starlette.status import HTTP_400_BAD_REQUEST
from src.utils import guess_exchange_and_ust
from src.utils import eod_ini_logic
from src.db import engines
from src.users.auth import bouncer
from src.users.auth import get_current_active_user
from src.users.user_models import UserPy
from starlette.responses import Response


router = fastapi.APIRouter()


@bouncer.roles_required('user')
@router.get(
    '/ivol/risk-reversal',
    summary='Get the risk reversal of fitted implied volatility data',
    operation_id='get_fitted_risk_reversal'
)
async def get_risk_reversal_fitted(
        symbol: str, ust: str = None,
        exchange: str = None,
        tte: tteChoices = tteChoices._1m,
        startdate: str = None,
        enddate: str = None,
        dminus: int = 30,
        delta1: deltaChoicesPractical = deltaChoicesPractical._d060,
        delta2: deltaChoicesPractical = deltaChoicesPractical._d040,
        order: OrderChoices = OrderChoices._asc,
        user: UserPy = fastapi.Depends(get_current_active_user)
):
    """
    Get the risk reversal of fitted implied volatility data for `symbol`.

    Essentially the risk reversal is a measure of the volatility skew.
    supplied only `offset` will be parsed.
    Minimally supply `symbol`. The backend will try to resolve the
    dependent query parameters such as security type `ust` and `exchange` or
    set defaults.

    Calculation:

    >rr = σ(delta1) - σ(delta2)

    Example:

    >delta1 = 60 (otm put with 40 delta)

    >delta2 = 40 (otm call with 40 delta)

    >rr = σ(|Δ_put| = 40) - σ(|Δ_call| = 40)

    For an average equities rr will be positive on average.

    - **symbol**: example: 'SPY' or 'spy' (case insensitive)
    - **ust**: underlying security type: ['fut', 'eqt', 'ind', 'fx']
    - **exchange**: one of: ['usetf', 'cme', 'ice', 'eurex']
    - **tte**: time until expiry. 1m 3m 12m ...
    - **startdate**: format: yyyymmdd
    - **enddate**: format: yyyymmdd
    - **dminus**: indicate the number of days back from `enddate`
    - **delta1**: manually set the first delta leg
    - **delta2**: manually set the second delta leg
    - **order**:  sorting order with respect to price interval
    """
    if delta1:
        delta1 = delta1.value
    if delta2:
        delta2 = delta2.value

    args = {
        'symbol': symbol,
        'ust': ust,
        'exchange': exchange,
        'tte': tte._value_,
        'startdate': startdate,
        'enddate': enddate,
        'dminus': dminus,
        'delta1': delta1,
        'delta2': delta2,
        'order': order.value
    }
    content = await resolve_me(args)
    return Response(content=content, media_type='application/json')


async def select_risk_reversal(args):
    """
    to create a quick testing SQL snippet try:
    args = {
    'offset': 50
    }
    Args:
        args: parsed arguments from API call

    """
    args = await guess_exchange_and_ust(args)
    args = await eod_ini_logic(args)
    if args['ust'] is None:
        return Response(
            content={'msg': f'Could not identify `ust` form symbol {args["symbol"]}'},
            status_code=HTTP_400_BAD_REQUEST
        )
    if args['exchange'] is None:
        return Response(
            content={'msg': f'Could not identify `exchange` form symbol {args["symbol"]}'},
            status_code=HTTP_400_BAD_REQUEST
        )
    args['tte'] = time_to_var_func(args['tte'])

    c = ContractSync()
    c.symbol = args['symbol']
    c.security_type = args['ust']
    c.exchange = args['exchange']

    c.target_table_name_base = c.compose_ivol_table_name_base()
    delta1 = args['delta1']
    delta2 = args['delta2']

    schema = c.compose_2_part_schema_name()
    table_first = c.compose_ivol_final_table_name(delta1)
    table_second = c.compose_ivol_final_table_name(delta2)
    sql = f'''
    WITH data AS (
        SELECT
            first.dt,
            first.{args['tte']} - second.{args['tte']} AS value
        FROM            {schema}.{table_first}  first
        FULL OUTER JOIN {schema}.{table_second} second 
            ON first.dt = second.dt 
        WHERE first.dt 
            BETWEEN '{args['startdate']}' 
            AND     '{args['enddate']}'
        ORDER BY first.dt {args['order']}
    )
    SELECT json_agg(data) FROM data;
    '''
    return sql


async def resolve_me(args):
    sql = await select_risk_reversal(args)
    async with engines['pgivbase'].acquire() as con:
        data = await con.fetch(sql)
        if len(data) != 0:
            return data[0].get('json_agg')
        else:
            return '[]'
