from collections import namedtuple
from datetime import datetime as dt
from datetime import date
from datetime import timedelta
from datetime import datetime as dt, timedelta
import fastapi
from falib.contract import Contract
from falib.const import time_to_var_func
from falib.const import OrderChoices
from falib.const import tteChoices
from falib.utils import guess_exchange_and_ust
from falib.utils import eod_ini_logic
from falib.db import engines

router = fastapi.APIRouter()


@router.get('/ivol/atm',
            summary='Get ATM implied volatility data'
)
async def atm_ivol(
        symbol: str, ust: str = None, exchange: str = None, tte: tteChoices = tteChoices._1m,
        startdate: str = None, enddate: str = None, dminus: int = 30,
        order: OrderChoices = OrderChoices._asc
):
    """
    At-the-money implied volatility time series.

    - **symbol**: example: 'SPY' or 'spy' (case insensitive)
    - **ust**: underlying security type: ['fut', 'eqt', 'ind', 'fx']
    - **exchange**: one of: ['usetf', 'cme', 'ice', 'eurex']
    - **tte**: time until expiry. 1m 3m 12m ...
    - **startdate**: format: yyyymmdd
    - **enddate**: format: yyyymmdd
    - **dminus**: indicate the number of days back from `enddate`
    - **order**:  sorting order with respect to price interval
    """
    args = {
        'symbol': symbol, 'ust': ust, 'exchange': exchange, 'tte': tte._value_,
        'startdate': startdate, 'enddate': enddate, 'dminus': dminus,
        'order': order.value
    }
    content = await resolve_atm_ivol(args)
    return content


AtmParams = namedtuple(
    'AtmParams',
    ['schema', 'table', 'varname', 'startdate', 'enddate', 'order', 'limit']
)


async def dpyd_atm_dispatcher(args):
    """ """
    args['delta'] = 'd050'
    limit = 350
    args = await guess_exchange_and_ust(args)
    args = await eod_ini_logic(args)
    c = Contract()
    c.symbol = args['symbol']
    c.exchange = args['exchange']
    c.security_type = args['ust']
    delta = args['delta']
    varname = time_to_var_func(args['tte'])
    #    if args['exchange'] == 'usetf':
    #        args['exchange'] = 'usmw'
    c.target_table_name_base = await c.compose_ivol_table_name_base()
    schema = await c.compose_2_part_schema_name()
    table = await c.compose_ivol_final_table_name(delta)
    params = AtmParams(
        schema=schema,
        table=table,
        varname=varname,
        startdate=args['startdate'],
        enddate=args['enddate'],
        order=args['order'],
        limit=limit)
    sql = await final_sql(params)
    return sql


async def final_sql(nt: AtmParams) -> str:
    return f'''
        SELECT dt, {nt.varname} AS value
        FROM {nt.schema}.{nt.table}  
        WHERE dt BETWEEN '{nt.startdate}' AND '{nt.enddate}'
        ORDER BY dt  {nt.order}
        LIMIT {nt.limit} ; 
    '''


async def resolve_atm_ivol(args):
    sql = await dpyd_atm_dispatcher(args)
    async with engines['t2'].acquire() as con:
        data = await con.fetch(query=sql)
        return data
