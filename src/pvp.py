from collections import namedtuple
from datetime import date as Date
import typing as t

from falib.contract import Contract
import fastapi
from fastapi import Depends
from fastapi.responses import ORJSONResponse
from pydantic import BaseModel
from sqlalchemy.orm.session import Session
from starlette import status
from starlette.exceptions import HTTPException

from src import const
from src.const import (
    IntervalUnitChoices,
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

router = fastapi.APIRouter()


class IntradayPvp(BaseModel):
    bucket: int
    sum_volume: int
    min_close: float
    max_close: float


@router.get(
    '/prices/intraday/pvp',
    operation_id='get_pvp_intraday',
    summary='price volume profile. histogram of intraday price data',
    response_model=t.List[IntradayPvp],
    response_class=ORJSONResponse,
)
async def get_pvp_intraday(
        symbol: str,
        month: futuresMonthChars = None,
        year: int = None,
        ust: str = None,
        exchange: str = None,
        startdate: Date = None,
        enddate: Date = None,
        dminus: int = 20,
        buckets: int = 100,
        iunit: IntervalUnitChoices = IntervalUnitChoices._minutes,
        order: OrderChoices = OrderChoices._asc,
        con: Session = Depends(get_prices_intraday_db),
        user: User = Depends(get_current_active_user),
):
    """
    price volume profile. histogram of intraday price data

    Creates equally spaced ``buckets`` number of well ... bucket ...
    from the highest to the lowest price price in the time period and
    sums the trading volume in the local price range specified by  ``max_close`` and ``min_close``.

    sample response:

    ```json
        [
          {"bucket": 1, "max_close": 362.17, "min_close": 362.17, "sum_volume": 435470},
          {"bucket": 2, "max_close": 362.3, "min_close": 362.29, "sum_volume": 658616},
          {"bucket": 4, "max_close": 362.5, "min_close": 362.49, "sum_volume": 880421},
          ...
          {"bucket": 100, "max_close": 372.32, "min_close": 372.25, "sum_volume": 630678},
          {"bucket": 101, "max_close": 372.34, "min_close": 372.34, "sum_volume": 179559}
        ]
    ```

    - **symbol**: example: 'SPY' or 'spy' (case insensitive)
    - **month**: only for futures - one of ['F', 'G', 'H', 'J', 'K', 'M', 'N', 'Q', 'U', 'V', 'X', 'Z']
    - **year**: only for futures - example: 19
    - **ust**: underlying security type: ['fut', 'eqt', 'ind', 'fx']
    - **exchange**: one of: ['usetf', 'cme', 'ice', 'eurex']
    - **startdate**: format: yyyy-mm-dd
    - **enddate**: format: yyyy-mm-dd
    - **dminus**: indicate the number of days back from `enddate`
    - **buckets**: number of intervals in the histogram
    - **iunit**: one of ['minutes', 'hour, 'day', 'week', 'month']
    - **order**:  sorting order with respect to price interval
    """
    args = {
        'symbol': symbol,
        'month': month.value,
        'year': year,
        'ust': ust,
        'exchange': exchange,
        'startdate': startdate,
        'enddate': enddate,
        'dminus': dminus,
        'buckets': buckets,
        'iunit': iunit.value,
        'order': order.value
    }
    content = await resolve_pvp(args, con)
    return content


pvpQueryParams = namedtuple(
    'pvpQueryParams',
    ['schema', 'table', 'startdate', 'enddate', 'buckets'])


async def pvp_query(args):
    """start_date end_date symbol c_month c_year exchange ust"""
    args = eod_ini_logic_new(args)
    args = guess_exchange_and_ust(args)
    if (
            args['ust'] == const.STR_UNDERLYING_SECURITY_TYPE_FUTURES
            and (args['year'] is None) or (args['month'] is None)
    ):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Specified future but did not provide both month and year parameters"
        )
    c = Contract()
    c.symbol = args['symbol']
    c.exchange = args['exchange']
    c.security_type = args['ust']

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
        buckets=args['buckets'],
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
    ORDER BY min_close;
    '''


async def resolve_pvp(args, con: Session):
    sql = await pvp_query(args)
    data = con.execute(sql).fetchall()
    return data
