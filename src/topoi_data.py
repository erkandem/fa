"""
currently the returned  data structure looks like:
 - compact, easy to subprocess
 - easy to
{
  "2019-10-01": {
    "24": 3,
    "25": 234,
    "26": 56,
    "27": 10,
    "35": 12
  }
}

self explaining way:
{
  "2019-10-01": {
    {"top": 1, "strike": 24: "volume": 3},
    {"top": 2, "strike": 25: "volume": 234},
    {"top": 3, "strike": 26: "volume": 56},
    {"top": 4, "strike": 27: "volume": 10},
    {"top": 5, "strike": 35: "volume": 10},
  }
}


"""
from datetime import datetime as dt
import re
import fastapi
from fastapi import Body
from fastapi import HTTPException
import pydantic
from fastapi.responses import ORJSONResponse
from pydantic import BaseModel
from starlette.responses import Response
from starlette.status import HTTP_400_BAD_REQUEST
from src.const import OrderChoices
from src.const import PutCallChoices
from src.const import iv_all_sym_choices, exchange_choices
from src.const import ust_choices
from src.const import dminusLimits
from src.db import engines

from src.utils import put_call_trafo
from src.utils import eod_ini_logic_new
from src.rawoption_data import get_schema_and_table_name
from fastapi import Depends
import typing as t
from sqlalchemy.orm.session import Session
from src.db import get_options_rawdata_db
from src.users import get_current_active_user, User

dml = dminusLimits(start=0, end=365*2)


class TopOiQuery(BaseModel):
    ust: str
    exchange: str
    symbol: str
    option_month: str = None
    underlying_month: str = None
    ltd: str
    startdate: str = None
    enddate: str = None
    dminus: int = 60
    putcall: PutCallChoices
    order: OrderChoices = OrderChoices._asc
    top_n: int = 5
    metric: str

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
        if v not in ['oi', 'volume']:
            raise ValueError('not a valid value for `metric`')
        return v

    @pydantic.validator('dminus')
    def dminus_validator(cls, v):
        if v < dml.start or v > dml.end:
            raise ValueError('not within a valid range of values for `dminus`')
        return v

    @pydantic.validator('top_n')
    def top_n_validator(cls, v):
        if v < 0 or v > 10:
            raise ValueError('not within a valid range of values for `top_n`')
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


router = fastapi.APIRouter()


@router.post(
    '/top-oi-and-volume',
    operation_id='post_top_oi_and_volume',
    response_class=ORJSONResponse,

)
async def post_top_oi_and_volume(
        query: TopOiQuery = Body(
            ...,
            example={
                "ust": "eqt",
                "exchange": "usetf",
                "symbol": "spy",
                "startdate": "2019-01-01",
                "enddate": "2019-04-01",
                "putcall": "call",
                "ltd": "20200117",
                "metric": "oi",
                "dminus": 365,
                "top_n": 5,
                "order": "desc"
            }
        ),
        con: Session = Depends(get_options_rawdata_db),
        user: User = Depends(get_current_active_user),
):
    """
    Returns the open interest development of the top `n` strikes of an option chain

    sample response for sample query
    ```
    {
      '2019-01-02': {
        '105': 20,
         '110': null,
         '115': null,
         '125': null,
         '135': 6
        },
      '2019-01-03': {
         '105': 20,
         '110': null,
         '115': null,
         '125': null,
          '135': 6
        },
        ...
    }
    ```

    """
    args = query.dict()
    if 'enddate' in args:
        if args['enddate']:
            args['enddate'] = dt.strptime(args['enddate'], '%Y-%m-%d')

    if 'startdate' in args:
        if args['startdate']:
            args['startdate'] = dt.strptime(args['startdate'], '%Y-%m-%d')

    data = await resolve_top_oi_or_volume(args, con)
    return data


async def resolve_top_oi_or_volume(args, con: Session):
    args = eod_ini_logic_new(args)
    args = await put_call_trafo(args)
    if args['ust'] == 'fut':
        if args['option_month'] is None and args['underlying_month'] is None:
            raise HTTPException(
                status_code=HTTP_400_BAD_REQUEST,
                detail="a query for futures requires `option_month` and `underlying_month`"
            )
    relation = await get_schema_and_table_name(args, con)
    if len(relation) != 2:
        return []  # "Could not find particular option chain.", 404
    args['schema'] = relation['schema']
    args['table'] = relation['table']
    sql = await top_x_oi_query(args)
    data = con.execute(sql).fetchall()
    if len(data) != 0 and len(data[0]) != 0:
        return data[0][0]
    else:
        return []


async def top_x_oi_query(args: {}) -> str:
    return f'''
          WITH ex AS (
                 SELECT   bizdt,
                          strkpx,
                          {args['metric']}
                 FROM     {args['schema']}.{args['table']}
                 WHERE    putcall = {args['putcall']}
                 AND      bizdt =
                          (
                                   SELECT   bizdt
                                   FROM     {args['schema']}.{args['table']}
                                   ORDER BY bizdt DESC LIMIT 1
                          )
                 -- comment start --
                 -- TODO: consider using average instead of implicitly using  
                 --       last value of `oi` or `volume`
                 -- TODO: enable sorting by `oi` or `volume`
                 -- TODO: enable "get top n after skipping top x"
                 ORDER BY oi DESC  
                 -- comment end -- 
                 LIMIT {args['top_n']}
        ), summary AS (
                 SELECT   t.bizdt,
                          t.strkpx,
                          t.{args['metric']} AS target_data
                 FROM     {args['schema']}.{args['table']} t
                 WHERE    t.strkpx IN
                          (
                                 SELECT strkpx
                                 FROM   ex
                          )
                 AND bizdt BETWEEN '{args['startdate']}' AND '{args['enddate']}'
                 AND      t.putcall = {args['putcall']}
                 ORDER BY t.bizdt,
                          t.{args['metric']} DESC
        ), resp AS (
                   SELECT     bizdt, 
                              -- first json wrapper
                              jsonb_object_agg(strkpx, target_data) AS target_data
                   FROM       summary 
                   -- replace missing values with 'null'
                   RIGHT JOIN (
                              (
                                    SELECT DISTINCT bizdt
                                    FROM            summary) a
                   CROSS JOIN
                              (
                                    SELECT DISTINCT strkpx
                                    FROM            summary) b) c
                   USING      (bizdt, strkpx)
                   GROUP BY   bizdt
                   ORDER BY   bizdt DESC) 
        -- second json wrapper
        SELECT jsonb_object_agg(bizdt, target_data)
        FROM   resp; 
        '''
