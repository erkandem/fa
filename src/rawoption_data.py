from datetime import datetime as dt
import re
import fastapi
import pydantic
from fastapi.responses import ORJSONResponse

from src.db import engines, results_proxy_to_list_of_dict
import typing as t

from src.const import ust_choices, dminusLimits
from src.const import RAWOPTION_MAP, exchange_choices
from src.const import metric_mapper_f
from src.const import iv_all_sym_choices
from src.utils import put_call_trafo
from src.const import RawDataMetricChoices, PutCallChoices, OrderChoices
from src.utils import CinfoQueries
from src.utils import eod_ini_logic_new
from pydantic import BaseModel
from sqlalchemy.orm.session import Session
from fastapi import Depends

from src.db import get_options_rawdata_db
from src.users import get_current_active_user, User

drl = dminusLimits(start=0, end=365*3)

router = fastapi.APIRouter()


class RawOption(BaseModel):
    ust: str
    exchange: str
    symbol: str
    option_month: str = None
    underlying_month: str = None
    ltd: str
    putcall: PutCallChoices
    strkpx: float
    metric: RawDataMetricChoices
    startdate: str
    enddate: str
    dminus: int = 30
    order: OrderChoices = OrderChoices._asc

    @pydantic.validator('symbol')
    def symbol_validator(cls, v):
        if v not in iv_all_sym_choices:
            raise ValueError('not a valid value for `symbol`')
        return v

    @pydantic.validator('ust')
    def ust_validator(cls, v):
        if v not in ust_choices:
            raise ValueError('not a valid value for `ust`')
        return v

    @pydantic.validator('exchange')
    def exchange_validator(cls, v):
        if v not in exchange_choices:
            raise ValueError('not a valid value for `exchange`')
        return v

    @pydantic.validator('metric')
    def metric_validator(cls, v):
        if v not in list(RAWOPTION_MAP):
            raise ValueError('not a valid value for `metric`')
        return v

    @pydantic.validator('dminus')
    def dminus_validator(cls, v):
        if v < drl.start or v > drl.end:
            raise ValueError('not within a valid range of values for `dminus`')
        return v

    @pydantic.validator('enddate')
    def enddate_validator(cls, v):
        if len(re.findall(r'^(\d{4}-\d{2}-\d{2})$', v)) == 0:
            raise ValueError('expected format:  yyyy-mm-dd')
        return v

    @pydantic.validator('startdate')
    def startdate_validator(cls, v):
        if len(re.findall(r'^(\d{4}-\d{2}-\d{2})$', v)) == 0:
            raise ValueError('expected format:  yyyy-mm-dd')
        return v

    @pydantic.validator('option_month')
    def option_month_validator(cls, v):
        if len(re.findall(r'^(\d{6})$', v)) == 0:
            raise ValueError('expected format:  yyyymm')
        return v

    @pydantic.validator('underlying_month')
    def underlying_month_validator(cls, v):
        if len(re.findall(r'^(\d{6})$', v)) == 0:
            raise ValueError('expected format:  yyyymm')
        return v


@router.post(
    '/option-data',
    operation_id='post_raw_option_data',
    response_class=ORJSONResponse,
)
async def post_raw_option_data(
        query: RawOption = fastapi.Body(
            ...,
            example={
                "ust": "eqt",
                "exchange": "usetf",
                "symbol": "spy",
                "putcall": "put",
                "ltd": "20200117",
                "metric": "rawiv",
                "strkpx": 250,
                "startdate": "2019-01-01",
                "enddate": "2019-04-01"
            }
        ),
        con: Session = Depends(get_options_rawdata_db),
        user: User = Depends(get_current_active_user),
):
    """
    time series data related to a single option
    (e.g. put on XYZ with strike at $123  expiring Jan 21, 2099)

    - **symbol**: example: 'SPY' or 'spy' (case insensitive)
    - **ust**: underlying security type: ['fut', 'eqt', 'ind', 'fx']
    - **exchange**: one of: ['usetf', 'cme', 'ice', 'eurex']
    - **option_month**: expiry month of the option chain format: yyyymm
    - **underlying_month**: maturity month of the underlying contract format: yyyymm
    - **startdate**: format: yyyy-mm-dd
    - **enddate**: format: yyyy-mm-dd
    - **dminus**: indicate the number of days back from `enddate`
    - **ltd**: last trading day of option chain. see info endpoint for choices. format: yyyymmdd
    - **putcall**: `put` or `call`
    - **strkpx**: strike price 125.5 ~ 125.49 e.g. will be recognized +1 minimum tick size
    - **metric**: choose one of the raw or derived data
    - **order**:  sorting order with respect to date

    Sample response for the metric ``rawiv``

    ```
    [
      {
        'dt': '2019-01-02',
         'rawiv': 0.193129145575342
      },
      {
        'dt': '2019-01-03',
        'rawiv': 0.19536307180984}
      },
      ...
    ]
    ```
    """
    args = query.dict()
    if 'enddate' in args:
        args['enddate'] = dt.strptime(args['enddate'], '%Y-%m-%d')
    if 'startdate' in args:
        args['startdate'] = dt.strptime(args['startdate'], '%Y-%m-%d')
    args['limit'] = 365
    data = await resolve_single_metric_raw_data(args, con)
    return data


async def final_sql(args: t.Dict[str, t.Any]):
    return f'''
        SELECT  bizdt as dt,
                {args['metric']} as {args['metric_out']}
        FROM    {args['schema']}.{args['table']}
        WHERE   putcall = {args['putcall']}
            AND strkpx = {args['strkpx']}
            AND bizdt BETWEEN '{args['startdate']}' AND '{args['enddate']}'
        ORDER BY dt
        LIMIT {args['limit']};
        '''


def resolve_schema_and_table_name_sql(args):
    if args['ust'] == 'fut':
        sql = CinfoQueries.get_schema_and_table_for_futures_sql(args)
    else:
        sql = CinfoQueries.get_table_and_schema_by_ltd(args)
    return sql


async def get_schema_and_table_name(args: t.Dict[str, t.Any], con: Session) -> t.Dict[str, str]:
    sql = resolve_schema_and_table_name_sql(args)
    cursor = con.execute(sql)
    relation = results_proxy_to_list_of_dict(cursor)
    if len(relation) != 0:
        return {
            'schema': relation[0].get('schema_name'),
            'table': relation[0].get('table_name'),
        }
    else:
        return {}


async def resolve_single_metric_raw_data(args: t.Dict[str, t.Any], con: Session):
    args = await put_call_trafo(args)
    relation = await get_schema_and_table_name(args, con)
    if len(relation) != 2:
        return []
    args = eod_ini_logic_new(args)
    args['metric_out'] = args['metric']
    args['metric'] = metric_mapper_f(args['metric'])
    args['schema'] = relation['schema']
    args['table'] = relation['table']
    sql = await final_sql(args)
    data = con.execute(sql).fetchall()
    return data
