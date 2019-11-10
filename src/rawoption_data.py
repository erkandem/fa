import re
import fastapi
from fastapi import Query
import pydantic
from pydantic import BaseModel
from src.db import engines
from src.const import ust_choices, dminusLimits
from src.const import RAWOPTION_MAP, exchange_choices
from src.const import metric_mapper_f
from src.const import iv_all_sym_choices
from src.utils import put_call_trafo
from src.const import RawDataMetricChoices, PutCallChoices, OrderChoices
from src.utils import CinfoQueries
from src.utils import eod_ini_logic

drl = dminusLimits(start=0, end=365)

router = fastapi.APIRouter()


class RawOptionPy(BaseModel):
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
        if len(re.findall(r'^(\d{8})$', v)) == 0:
            raise ValueError('expected format:  yyyymmdd')
        return v

    @pydantic.validator('startdate')
    def startdate_validator(cls, v):
        if len(re.findall(r'^(\d{8})$', v)) == 0:
            raise ValueError('expected format:  yyyymmdd')
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
    operation_id='post_raw_option_data'
)
async def post_raw_option_data(
        query: RawOptionPy = fastapi.Body(
            ...,
            example={
                "ust": "eqt",
                "exchange": "usetf",
                "symbol": "spy",
                "putcall": "put",
                "ltd": "20200117",
                "metric": "rawiv",
                "strkpx": 250,
                "startdate": "20190101",
                "enddate": "20190401"
            }
        )
        #, user: UserPy = fastapi.Depends(get_current_active_user)
):
    """
    time series data related to a single option
    (e.g. put on XYZ with strike at $123  expiring Jan 21, 2099)

    - **symbol**: example: 'SPY' or 'spy' (case insensitive)
    - **ust**: underlying security type: ['fut', 'eqt', 'ind', 'fx']
    - **exchange**: one of: ['usetf', 'cme', 'ice', 'eurex']
    - **option_month**: expiry month of the option chain format: yyyymm
    - **underlying_month**: maturity month of the underlying contract format: yyyymm
    - **startdate**: format: yyyymmdd
    - **enddate**: format: yyyymmdd
    - **dminus**: indicate the number of days back from `enddate`
    - **ltd**: last trading day of option chain. see info endpoint for choices. format: yyyymmdd
    - **putcall**: `put` or `call`
    - **strkpx**: strike price 125.5 ~ 125.49 e.g. will be recognized +1 minimum tick size
    - **metric**: choose one of the raw or derived data
    - **order**:  sorting order with respect to date

    """
    args = query.dict()
    data = await resolve_single_metric_raw_data(args)
    return data


async def final_sql(args):
    return f'''
        SELECT  bizdt as dt,
                {args['metric']} as {args['metric_out']}
        FROM    {args['schema']}.{args['table']}
        WHERE   putcall = {args['putcall']}
            AND strkpx = {args['strkpx']}
            AND bizdt BETWEEN '{args['startdate']}' AND '{args['enddate']}'
        ORDER BY dt
        LIMIT 250;
        '''


async def get_schema_and_table_name(args: {}) -> {}:
    if args['ust'] == 'fut':
        return await get_schema_and_table_name_for_futures(args)
    else:
        return await get_schema_and_table_for_not_fut(args)


async def get_schema_and_table_name_for_futures(args):
    sql = CinfoQueries.get_schema_and_table_for_futures_sql(args)
    async with engines['yh'].acquire() as con:
        relation = await con.fetch(sql)
        if len(relation) != 0:
            return {
                'schema': relation[0].get('schema_name'),
                'table': relation[0].get('table_name')
            }
        else:
            return []


async def get_schema_and_table_for_not_fut(args):
    sql = CinfoQueries.get_table_and_schema_by_ltd(args)
    async with engines['yh'].acquire() as con:
        relation = await con.fetch(sql)
        if len(relation) != 0:
            return {
                'schema': relation[0].get('schema_name'),
                'table': relation[0].get('table_name')
            }
        else:
            return []


async def resolve_single_metric_raw_data(args):
    args = await put_call_trafo(args)
    relation = await get_schema_and_table_name(args)
    if len(relation) != 2:
        return []
    args = await eod_ini_logic(args)
    args['metric_out'] = args['metric']
    args['metric'] = metric_mapper_f(args['metric'])
    args['schema'] = relation['schema']
    args['table'] = relation['table']
    sql = await final_sql(args)
    async with engines['yh'].acquire() as con:
        data = await con.fetch(sql)
        return data
