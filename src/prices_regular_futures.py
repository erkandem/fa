from collections import namedtuple
from datetime import date as Date
from datetime import datetime as dt
import typing as t

from falib.contract import Contract
from fastapi import (
    APIRouter,
    Depends,
)
from fastapi.responses import ORJSONResponse
from pydantic import BaseModel
from sqlalchemy.orm.session import Session
from starlette import status
from starlette.exceptions import HTTPException

from src.const import (
    OrderChoices,
    futuresMonthChars,
)
from src.db import get_prices_intraday_db
from src.users import (
    User,
    get_current_active_user,
)
from src.utils import (
    eod_ini_logic_new,
    guess_exchange_and_ust,
)

router = APIRouter()

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
    response_class=ORJSONResponse,
)
async def get_regular_futures_eod(
        symbol: str,
        month: futuresMonthChars = futuresMonthChars._z,
        year: int = dt.now().year + 1,
        ust: str = None,
        exchange: str = None,
        startdate: Date = None,
        enddate: Date = None,
        dminus: int = 30,
        order: OrderChoices = OrderChoices._asc,
        con: Session = Depends(get_prices_intraday_db),
        user: User = Depends(get_current_active_user),
):
    """
    end of day prices for futures contracts
    ``year``has to be four digit number.
    """
    if len(str(year)) != 4:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="expecting year parameter to be a four digit number"
        )
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
