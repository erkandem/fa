from datetime import datetime as dt
from datetime import date
from datetime import timedelta
from datetime import datetime as dt, timedelta
from collections import namedtuple
from falib.const import time_to_var
from falib.contract import Contract
from falib.db import engines
from falib.utils import guess_ust_from_symbol_intraday
from falib.utils import guess_exchange_and_ust
from falib.utils import eod_ini_logic

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
    varname = time_to_var[args['tte']]
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