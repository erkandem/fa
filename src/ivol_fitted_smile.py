from collections import namedtuple
from datetime import datetime as dt
from datetime import date
from datetime import timedelta
import fastapi
from falib.contract import Contract
from src.const import time_to_var_func
from src.const import OrderChoices
from src.const import tteChoices
from src.utils import guess_exchange_and_ust
from src.utils import eod_ini_logic
from src.db import engines
from src.users.auth import bouncer
from src.users.auth import get_current_active_user
from src.users.user_models import UserPy
from falib.contract import ContractSync
from starlette.responses import Response

router = fastapi.APIRouter()


@bouncer.roles_required('user')
@router.get(
    '/ivol/smile',
    summary='smile',
    operation_id='get_ivol_smile'
)
async def get_ivol_smile(
        symbol: str,
        ust: str = None,
        exchange: str = None,
        tte: tteChoices = tteChoices._1m,
        startdate: str = None,
        enddate: str = None,
        dminus: int = 30,
        order: OrderChoices = OrderChoices._asc,
        user: UserPy = fastapi.Depends(get_current_active_user)
):
    """
    `smile` is defined as the implied volatility curve of one expiry at one date.
    The curve being the implied volatility from out-of-the-money puts to out-of-the-money calls.

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
    data = await resolve_ivol_fitted_smile(args)
    return Response(content=data, media_type='application/json')


async def select_ivol_fitted_smile(args):
    """
    import asyncio
    from src.ivol_fitted_smile import select_ivol_fitted_smile

    from datetime import datetime as dt
    args = dict()
    args['tte'] = '1m'
    args['symbol'] = 'cl'
    args['exchange'] = 'cme'
    args['ust'] = 'fut'
    args['startdate'] = '20190501'
    args['enddate'] = '20191201'

    print(asyncio.run(select_ivol_fitted_smile(args)))


    Args:
        args:

    """
    args = await guess_exchange_and_ust(args)
    args = await eod_ini_logic(args)
    args['tte'] = time_to_var_func(args['tte'])
    if args['exchange'] == 'usetf':
        args['exchange'] = 'usmw'
    c = ContractSync()
    c.symbol = args['symbol']
    c.exchange = args['exchange']
    c.security_type = args['ust']
    c.target_table_name_base = c.compose_ivol_table_name_base()
    schema = c.compose_2_part_schema_name()
    sql_code = f'''
    WITH raw_data AS (
    SELECT  d010.dt,
            d010.{args['tte']} AS d010,
            d015.{args['tte']} AS d015,
            d020.{args['tte']} AS d020,
            d025.{args['tte']} AS d025,
            d030.{args['tte']} AS d030,
            d035.{args['tte']} AS d035,
            d040.{args['tte']} AS d040,
            d045.{args['tte']} AS d045,
            d050.{args['tte']} AS d050,
            d055.{args['tte']} AS d055,
            d060.{args['tte']} AS d060,
            d065.{args['tte']} AS d065,
            d070.{args['tte']} AS d070,
            d075.{args['tte']} AS d075,
            d080.{args['tte']} AS d080,
            d085.{args['tte']} AS d085,
            d090.{args['tte']} AS d090
    FROM    {schema}.{c.compose_ivol_final_table_name('d010')} d010
    FULL OUTER JOIN {schema}.{c.compose_ivol_final_table_name('d015')} d015 ON d010.dt = d015.dt
    FULL OUTER JOIN {schema}.{c.compose_ivol_final_table_name('d020')} d020 ON d010.dt = d020.dt
    FULL OUTER JOIN {schema}.{c.compose_ivol_final_table_name('d025')} d025 ON d010.dt = d025.dt
    FULL OUTER JOIN {schema}.{c.compose_ivol_final_table_name('d030')} d030 ON d010.dt = d030.dt
    FULL OUTER JOIN {schema}.{c.compose_ivol_final_table_name('d035')} d035 ON d010.dt = d035.dt
    FULL OUTER JOIN {schema}.{c.compose_ivol_final_table_name('d040')} d040 ON d010.dt = d040.dt
    FULL OUTER JOIN {schema}.{c.compose_ivol_final_table_name('d045')} d045 ON d010.dt = d045.dt
    FULL OUTER JOIN {schema}.{c.compose_ivol_final_table_name('d050')} d050 ON d010.dt = d050.dt
    FULL OUTER JOIN {schema}.{c.compose_ivol_final_table_name('d055')} d055 ON d010.dt = d055.dt
    FULL OUTER JOIN {schema}.{c.compose_ivol_final_table_name('d060')} d060 ON d010.dt = d060.dt
    FULL OUTER JOIN {schema}.{c.compose_ivol_final_table_name('d065')} d065 ON d010.dt = d065.dt
    FULL OUTER JOIN {schema}.{c.compose_ivol_final_table_name('d070')} d070 ON d010.dt = d070.dt
    FULL OUTER JOIN {schema}.{c.compose_ivol_final_table_name('d075')} d075 ON d010.dt = d075.dt
    FULL OUTER JOIN {schema}.{c.compose_ivol_final_table_name('d080')} d080 ON d010.dt = d080.dt
    FULL OUTER JOIN {schema}.{c.compose_ivol_final_table_name('d085')} d085 ON d010.dt = d085.dt
    FULL OUTER JOIN {schema}.{c.compose_ivol_final_table_name('d090')} d090 ON d010.dt = d090.dt
    WHERE d010.dt BETWEEN '{args['startdate']}' AND '{args['enddate']}'
    ORDER BY dt
    ) SELECT json_agg(raw_data) AS smile_ts FROM raw_data;
    '''
    return sql_code


async def resolve_ivol_fitted_smile(args):
    sql = await select_ivol_fitted_smile(args)
    async with engines['pgivbase'].acquire() as con:
        data = await con.fetch(sql)
        if len(data) != 0:
            return data[0].get('smile_ts')
        else:
            return '[]'
