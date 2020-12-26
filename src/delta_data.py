from datetime import datetime as dt
import re
import fastapi
import pydantic
from fastapi import Body

from src.const import iv_all_sym_choices, exchange_choices
from src.users import get_current_active_user, User
from src.utils import eod_ini_logic_new
from src.rawoption_data import get_schema_and_table_name
from src.const import ust_choices
from src.db import get_options_rawdata_db, results_proxy_to_list_of_dict
from fastapi import Depends
import typing as t
from pydantic import BaseModel
from sqlalchemy.orm.session import Session

class DeltaQuery(BaseModel):
    ust: str
    exchange: str
    symbol: str
    option_month: str = None
    underlying_month: str = None
    ltd: str
    startdate: str
    enddate: str

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

    @pydantic.validator('startdate')
    def startdate_validator(cls, v):
        if len(re.findall(r'^(\d{4}-\d{2}-\d{2})$', v)) == 0:
            raise ValueError('expected format:  yyyy-mm-dd')
        return v

    @pydantic.validator('enddate')
    def enddate_validator(cls, v):
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

response_model = t.Dict[str, t.Dict[str, t.Union[float, None]]]


@router.post(
    '/delta-contour',
    operation_id='post_delta_data',
)
async def post_delta_data(
        query: DeltaQuery = Body(
            ...,
            example={
                "ust": "fut",
                "exchange": "cme",
                "symbol": "cl",
                "option_month": "201912",
                "underlying_month": "201912",
                "startdate": "2019-01-01",
                "enddate": "2019-04-01",
                "ltd": "20191115"
            }
        ),
        con: Session = Depends(get_options_rawdata_db),
        user: User = Depends(get_current_active_user),
):
    """
    Sample Response (includes `null`s):

    ```json
    {
      "2019-01-02": {
        "15": 0.997529599040824,
        "20": 0.989729380073849,
        "30": 0.935990764207618,
        "40": 0.794768083771764,
        "50": 0.583851075903858,
        "60": 0.347603220495328,
        "70": 0.187799489093798,
        "80": 0.0967965610201772,
        "90": 0.0530439215416349,
        "100": 0.0291585390742281,
        "110": 0.0177133030709603,
        "115": 0.012832594747696,
        "120": 0.00943424268115006,
        "125": 0.00760777234539778,
        "130": 0.0058177633358902
      },
      "2019-01-03": {
        "15": 0.997529599040824,
        "20": 0.989729380073849,
        "30": 0.935990764207618,
        "40": 0.794768083771764,
        "50": 0.583851075903858,
        "60": 0.347603220495328,
        "70": 0.187799489093798,
        "80": 0.0967965610201772,
        "90": 0.0530439215416349,
        "100": 0.0291585390742281,
        "110": 0.0177133030709603,
        "115": 0.012832594747696,
        "120": 0.00943424268115006,
        "125": 0.00760777234539778,
        "130": 0.0058177633358902
      }
    }
    ```
    """
    args = query.dict()
    if 'enddate' in args:
        args['enddate'] = dt.strptime(args['enddate'], '%Y-%m-%d')

    if 'startdate' in args:
        args['startdate'] = dt.strptime(args['startdate'], '%Y-%m-%d')

    data = await resolve_delta_query(args, con)
    return data


async def resolve_delta_query(args: {}, con: Session):
    args = eod_ini_logic_new(args)
    relation = await get_schema_and_table_name(args, con)
    if len(relation) != 2:
        return []  # "Could not find particular option chain.", 404
    args['schema'] = relation['schema']
    args['table'] = relation['table']
    sql = delta_query_sql(**args)
    cursor = con.execute(sql)
    data = results_proxy_to_list_of_dict(cursor)
    if len(data) != 0:
        return data[0].get('jsonb_object_agg')
    else:
        return []


def delta_query_sql(
        *,
        schema: str,
        table: str,
        startdate: str,
        enddate: str,
        **kwargs
):
    """
    Args:
        schema (str):
        table (str):
        startdate (str):
        enddate (str):

    """
    return f'''
    WITH ex AS (
        SELECT bizdt, strkpx, delta, moneyness, putcall
        FROM {schema}.{table}
    -------------- (select the last LIMIT days  -------------
        WHERE bizdt BETWEEN '{startdate}' AND '{enddate}'
        ORDER BY bizdt, strkpx DESC 
    ), smry AS (
        ---------- apply different filtering with -----------
        ---------- respect to delta and moneyness -----------
        ---------- depending on put or call -----------------
        (    
            SELECT   bizdt, putcall, strkpx, delta + 1 as delta, moneyness
            FROM ex
            WHERE bizdt  IN (SELECT DISTINCT bizdt FROM ex ORDER BY bizdt DESC)
                AND moneyness >= 0
                AND putcall = 0
            ORDER BY strkpx DESC 
        ) UNION ALL (
            SELECT bizdt, putcall, strkpx, delta, moneyness
            FROM ex
            WHERE bizdt IN (SELECT DISTINCT bizdt FROM ex ORDER BY bizdt DESC)
                AND moneyness < 0
                AND putcall = 1
            ORDER BY strkpx DESC
        ) 
    ), resp AS (
        ---------------- first JSON wrapper --------------------------
        SELECT bizdt, jsonb_object_agg(strkpx, delta) AS delta
        FROM smry
        --------------- replace missing values with 'null' -----------
        RIGHT JOIN (
            (SELECT DISTINCT bizdt FROM smry) a
            CROSS JOIN
            (SELECT DISTINCT strkpx FROM smry ORDER BY strkpx) b
           ) c
           USING      (bizdt, strkpx)
           GROUP BY   bizdt
           ORDER BY   bizdt DESC
    )
    --------------- final select and JSON wrapper -------------------
    SELECT jsonb_object_agg(bizdt, delta) FROM resp; 
    --------------------- and we are done ---------------------------
    '''
