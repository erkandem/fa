from collections import namedtuple
from datetime import datetime as dt
from datetime import timedelta
from datetime import date
import fastapi
from pydantic import BaseModel
from starlette.status import HTTP_200_OK
from falib.contract import Contract
from falib.const import OrderChoices
from falib.const import ust_choices_intraday
from falib.const import exchange_choices_intraday
from falib.const import futures_month_chars
from falib.const import prices_intraday_all_symbols
from falib.utils import guess_exchange_and_ust
from falib.utils import eod_ini_logic
from falib.db import engines


router = fastapi.APIRouter()

RegularFuturesParams = namedtuple(
    'regularaFuturesParams',
    ['schema', 'table', 'startdate', 'enddate', 'order', 'limit'])


@router.get('/prices/eod')
async def get_regular_futures_eod(
        symbol: str, month: int = None, year: int = None, ust: str = None, exchange: str = None,
        startdate: str = None, enddate: str = None, dminus: int = 30,
        order: OrderChoices = OrderChoices._asc
):
    """prices """
    args = {
        'symbol': symbol, 'month': month, 'year': year, 'ust': ust, 'exchange': exchange,
        'startdate': startdate, 'enddate': enddate, 'dminus': dminus, 'order': order.value
    }
    content = await resolve_eod_futures(args)
    return content

async def eod_sql_delivery(args):
    """TODO fix the table name creation which should be handled by the Contract class"""
    args = await guess_exchange_and_ust(args)
    c = Contract()
    c.symbol = args['symbol']
    c.exchange = args['exchange']
    c.security_type = args['ust']
    args = await eod_ini_logic(args)
    schema = f"{args['ust']}_{args['exchange']}_eod"
    contract = f"{args['symbol']}{args['month']}{args['year']}".lower()
    table = f"{args['ust']}_{args['exchange']}_{contract}_eod"
    limit = 365
    params = RegularFuturesParams(
        schema=schema, table=table,
        startdate=args['startdate'], enddate=args['enddate'],
        order=args['order'],
        limit=limit
    )
    sql = await final_sql(params)
    return sql


async def final_sql(nt: RegularFuturesParams) -> str:
    return  f'''
        SELECT * 
        FROM {nt.schema}.{nt.table}
        WHERE dt  BETWEEN '{nt.startdate}' AND '{nt.enddate}'
        ORDER BY dt {nt.order}
        LIMIT {nt.limit}; 
    '''


async def resolve_eod_futures(args):
    sql = await eod_sql_delivery(args)
    async with engines['prices'].acquire() as con:
        data = await con.fetch(query=sql)
        return data
