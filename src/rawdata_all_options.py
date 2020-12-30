from datetime import date as Date
from enum import Enum
import json
import typing as t

from falib.contract import ContractSync
from falib.dayindex import (
    get_day_index_schema_name,
    get_day_index_table_name,
)
import fastapi
from fastapi import (
    Depends,
    Header,
)
from fastapi.responses import ORJSONResponse
from sqlalchemy.orm.session import Session
from starlette.exceptions import HTTPException
from starlette.responses import Response
from starlette.status import HTTP_204_NO_CONTENT

from src.db import (
    get_options_rawdata_db,
    results_proxy_to_list_of_dict,
)
from src.users import (
    User,
    get_current_active_user,
)
from src.utils import guess_exchange_and_ust

router = fastapi.APIRouter()


class ContentType(str, Enum):
    json: str = 'application/json'
    csv: str = 'application/csv'


@router.get(
    '/option-data/single-underlying-single-day',
    summary='Returns all options for one underlying for one (business)day',
    operation_id='get_all_options_single_underlying_single_day',
)
async def get_all_options_single_underlying_single_day(
        symbol: str,
        date: Date,
        ust: str = None,
        exchange: str = None,
        accept: ContentType = Header(default=ContentType.json),
        con: Session = Depends(get_options_rawdata_db),
        user: User = Depends(get_current_active_user),
):
    """
    A route template. Will set appropriate headers and forward
    the already serialized postgres response.

    Currently only for ETFs (e.g. symbol='spy')

    - **symbol**: example: 'SPY' or 'spy' (case insensitive)
    - **ust**: underlying security type: 'eqt' e.g.
    - **exchange**: one of: 'usetf', e.g.
    - **date**: format: yyyy-mm-dd
    """
    args = {
        'symbol': symbol,
        'ust': ust,
        'exchange': exchange,
        'date': date
    }
    data = await resolve_options_data(args, con)
    if accept.value == 'application/json':
        content = json.dumps(data)
        return ORJSONResponse(content=content, media_type='application/json')
    if accept.value == 'application/csv':
        content = await to_csv(data)
        return Response(content=content, media_type='application/csv')
    content = json.dumps(data)
    return ORJSONResponse(content=content, media_type='application/json')


async def to_csv(json_data: t.Dict[str, t.Any]) -> str:
    """
    will convert a JSON-string to a CSV-string
    expected schema is [{"key": "value"}]
    where `value` may be `int` or `str`
    """
    if len(json_data) == 0:
        return ''
    keys = list(json_data[0])
    csv = (
            ','.join(keys)
            + '\n'
            + '\n'.join([
                ','.join([str(row[key]) for key in keys])
                for row in json_data
                ])
    )
    return csv


async def get_all_relations(args: t.Dict, con: Session):
    """
    will query the index table for all table names which
    have a record for a certain business day
    also used in the fitting in local project `py_markets`
    """
    c = ContractSync(
        symbol=args['symbol'],
        security_type=args['ust'],
        exchange=args['exchange']
    )
    schema = get_day_index_schema_name()
    table = get_day_index_table_name(c.compose_3_part_schema_name())
    sql = f'''
        SELECT DISTINCT name
        FROM {schema}.{table}
        WHERE bizdt = '{args["date"]}';
    '''
    relations = con.execute(sql).fetchall()
    return relations


async def select_union_all_ltds(args, con):
    """
    will compose a postgres specific SQL command
    which will return the data as a JSON-string
    """
    args = guess_exchange_and_ust(args)
    if isinstance(args['date'], Date):
        args['date'] = args['date'].strftime('%Y-%m-%d')
    relations = await get_all_relations(args, con)
    if len(relations) == 0:
        raise HTTPException(
            status_code=HTTP_204_NO_CONTENT,
            detail=f'not data for selected date `{args["date"]}`'
        )
    c = ContractSync(
        symbol=args['symbol'],
        security_type=args['ust'],
        exchange=args['exchange']
    )
    schema = c.compose_3_part_schema_name()
    sql = 'WITH data AS ('
    for n, record in enumerate(relations):
        sql += f'''(
            SELECT
                bizdt, undprice, putcall,
                strkpx, settleprice, volume,
                oi, yte, moneyness,
                divyield, rfr, rawiv,
                delta, tv
            FROM {schema}.{record['name']}
            WHERE bizdt = '{args["date"]}'
        '''
        if n != len(relations) - 1:
            sql += ') UNION ALL '
        else:
            sql += ')'
    sql += '''        )
        SELECT json_agg(data) FROM data;
        '''
    return sql


async def resolve_options_data(args: t.Dict[str, t.Any], con: Session):
    sql = await select_union_all_ltds(args, con)
    cursor = con.execute(sql)
    data = results_proxy_to_list_of_dict(cursor)
    if len(data) != 0:
        return data[0].get('json_agg')
    else:
        return []
