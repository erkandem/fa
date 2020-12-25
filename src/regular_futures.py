from collections import namedtuple
from datetime import datetime as dt
from datetime import timedelta
from datetime import date as Date
import fastapi
from falib.contract import Contract
from src.const import OrderChoices
from src.utils import guess_exchange_and_ust
from src.utils import eod_ini_logic_new
import typing as t
from sqlalchemy.orm.session import Session
from src.db import get_prices_intraday_db
from fastapi import Depends
from src.db import results_proxy_to_list_of_dict
from pydantic import BaseModel


router = fastapi.APIRouter()

RegularFuturesParams = namedtuple(
    'regularFuturesParams',
    ['schema', 'table', 'startdate', 'enddate', 'order', 'limit'])


class RegularFuturesEod(BaseModel):
    dt: Date
    open: float
    high: float
    low: float
    close: float
    volume: int
    oi: int


@router.get(
    '/prices/eod',
    operation_id='get_regular_futures_eod',
    response_model=t.List[RegularFuturesEod],
)
async def get_regular_futures_eod(
        symbol: str,
        month: str = None,
        year: int = None,
        ust: str = None,
        exchange: str = None,
        startdate: Date = None,
        enddate: Date = None,
        dminus: int = 30,
        order: OrderChoices = OrderChoices._asc,
        con: Session = Depends(get_prices_intraday_db),
):
    """end of day prices """
    args = {
        'symbol': symbol,
        'month': month,
        'year': year,
        'ust': ust,
        'exchange': exchange,
        'startdate': startdate,
        'enddate': enddate,
        'dminus': dminus,
        'order': order.value,
    }
    content = await resolve_eod_futures(args, con)
    return content


async def eod_sql_delivery(args):
    """TODO fix the table name creation which should be handled by the Contract class"""
    args = eod_ini_logic_new(args)
    args = guess_exchange_and_ust(args)
    c = Contract()
    c.symbol = args['symbol']
    c.exchange = args['exchange']
    c.security_type = args['ust']
    schema = f"{args['ust']}_{args['exchange']}_eod"
    contract = f"{args['symbol']}{args['month']}{args['year']}".lower()
    table = f"{args['ust']}_{args['exchange']}_{contract}_prices_eod"
    limit = 365 * 2
    params = RegularFuturesParams(
        schema=schema, table=table,
        startdate=args['startdate'], enddate=args['enddate'],
        order=args['order'],
        limit=limit
    )
    sql = await final_sql(params)
    return sql


async def final_sql(nt: RegularFuturesParams) -> str:
    return f'''
        SELECT * 
        FROM {nt.schema}.{nt.table}
        WHERE dt  BETWEEN '{nt.startdate}' AND '{nt.enddate}'
        ORDER BY dt {nt.order}
        LIMIT {nt.limit}; 
    '''


async def resolve_eod_futures(args, con: Session):
    sql = await eod_sql_delivery(args)
    data = con.execute(sql).fetchall()
    return data
