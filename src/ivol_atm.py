from datetime import date as Date
import fastapi
from falib.contract import Contract
from src.const import time_to_var_func
from src.const import OrderChoices
from src.const import tteChoices
from src.const import deltaChoicesPractical
from appconfig import engines
from src.utils import guess_exchange_and_ust
from src.utils import eod_ini_logic_new

router = fastapi.APIRouter()


@router.get(
    '/ivol',
    summary='Get implied volatility data for a single delta and single tte',
    operation_id='get_ivol'
)
async def get_ivol(
        symbol: str,
        ust: str = None,
        exchange: str = None,
        startdate: Date = None,
        enddate: Date = None,
        dminus: int = 30,
        tte: tteChoices = tteChoices._1m,
        delta: deltaChoicesPractical = deltaChoicesPractical._d050,
        order: OrderChoices = OrderChoices._asc,
):
    """
    implied volatility time series. Return a proxy for ATM by default
    Default: d050 which is identical to the /ivol/atm route


    - **symbol**: example: 'SPY' or 'spy' (case insensitive)
    - **ust**: underlying security type: ['fut', 'eqt', 'ind', 'fx']
    - **exchange**: one of: ['usetf', 'cme', 'ice', 'eurex']
    - **startdate**: format: yyyy-mm-dd
    - **enddate**: format: yyyy-mm-dd
    - **dminus**: indicate the number of days back from `enddate`
    - **tte**: time until expiry. 1m 3m 12m ...
    - **delta**: e.g. d050 (default)
    - **order**:  sorting order with respect  to date
    """
    args = {
        'symbol': symbol,
        'ust': ust,
        'exchange': exchange,
        'startdate': startdate,
        'enddate': enddate,
        'dminus': dminus,
        'tte': tte._value_,
        'delta': delta.value,
        'order': order.value
    }
    content = await resolve_ivol(args)
    return content


@router.get(
    '/ivol/atm',
    summary='Get ATM implied volatility data',
    operation_id='get_atm_ivol'
)
async def atm_ivol(
        symbol: str,
        ust: str = None,
        exchange: str = None,
        tte: tteChoices = tteChoices._1m,
        startdate: Date = None,
        enddate: Date = None,
        dminus: int = 30,
        order: OrderChoices = OrderChoices._asc,
):
    """
    At-the-money implied volatility time series.

    - **symbol**: example: 'SPY' or 'spy' (case insensitive)
    - **ust**: underlying security type: ['fut', 'eqt', 'ind', 'fx']
    - **exchange**: one of: ['usetf', 'cme', 'ice', 'eurex']
    - **tte**: time until expiry. 1m 3m 12m ...
    - **startdate**: format: yyyy-mm-dd
    - **enddate**: format: yyyy-mm-dd
    - **dminus**: indicate the number of days back from `enddate`
    - **order**:  sorting order with respect to date
    """
    args = {
        'symbol': symbol,
        'ust': ust,
        'exchange': exchange,
        'startdate': startdate,
        'enddate': enddate,
        'dminus': dminus,
        'tte': tte._value_,
        'delta': deltaChoicesPractical._d050.value,
        'order': order.value
    }
    content = await resolve_ivol(args)
    return content


async def select_ivol(args):
    """ """
    args = await eod_ini_logic_new(args)
    args = await guess_exchange_and_ust(args)
    c = Contract()
    c.symbol = args['symbol']
    c.exchange = args['exchange']
    c.security_type = args['ust']
    delta = args['delta']
    args['tte'] = time_to_var_func(args['tte'])

    c.target_table_name_base = await c.compose_ivol_table_name_base()
    schema = await c.compose_2_part_schema_name()
    table = await c.compose_ivol_final_table_name(delta)
    sql = f'''
        SELECT dt, {args['tte']} AS value
        FROM {schema}.{table}  
        WHERE dt BETWEEN '{args['startdate']}' AND '{args['enddate']}'
        ORDER BY dt  {args['order']}; 
    '''
    return sql


async def resolve_ivol(args):
    sql = await select_ivol(args)
    async with engines.pgivbase.acquire() as con:
        data = await con.fetch(query=sql)
        return data
