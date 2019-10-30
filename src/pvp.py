from collections import namedtuple
from datetime import datetime as dt, timedelta
from falib.db import engines
from falib.utils import guess_exchange_and_ust
from falib.utils import eod_ini_logic
from falib.contract import Contract

pvpQueryParams = namedtuple(
    'pvpQueryParams',
    ['schema', 'table', 'startdate', 'enddate', 'buckets'])

async def pvp_query(args):
    """start_date end_date symbol c_month c_year exchange ust"""
    args = await guess_exchange_and_ust(args)
    c = Contract()
    c.symbol = args['symbol']
    c.exchange = args['exchange']
    c.security_type = args['ust']
    args = await eod_ini_logic(args)
    if args['year'] is not None:
        c.contract_yyyy = 2000 + args['year']
    if args['month'] is not None:
        c.contract_month = args['month']
    if c.contract_month and c.contract_yyyy:
        c.contract = f'''{args['symbol']}{args['month']}{args['year']}'''.lower()
    schema = await c.compose_2_part_schema_name()
    table = await c.compose_prices_intraday_table_name()
    params = pvpQueryParams(
        schema=schema, table=table,
        startdate=args['startdate'], enddate=args['enddate'],
        buckets=args['buckets']
    )
    sql = await final_sql(params)
    return sql


async def final_sql(nt: pvpQueryParams) -> str:
    return f'''

    WITH mima AS (
            SELECT    MIN(close_value) AS abs_min, 
                      MAX(close_value)  AS abs_max 
            FROM      {nt.schema}.{nt.table} 
            WHERE dt BETWEEN '{nt.startdate}' AND  '{nt.enddate}' 
        ) 
    SELECT  width_bucket(
                tab.close_value,
                    (SELECT abs_min FROM mima LIMIT 1),
                    (SELECT abs_max FROM mima LIMIT 1),
                    {nt.buckets}
                ) 
                AS bucket,
            SUM(tab.volume_value) AS sum_volume, 
            MIN(tab.close_value) AS min_close, 
            MAX(tab.close_value) AS max_close 
    FROM      {nt.schema}.{nt.table} tab 
    WHERE    tab.dt BETWEEN '{nt.startdate}' AND  '{nt.enddate}' 
    GROUP BY bucket 
    ORDER BY min_close ASC; 
    '''


async def resolve_pvp(args):
    sql = await pvp_query(args)
    async with engines['prices'].acquire() as con:
        data = await con.fetch(query=sql)
        return data
