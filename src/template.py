from datetime import date as Date
import typing as t

from databases.core import Connection
from fastapi import (
    APIRouter,
    Depends,
)
from starlette.responses import Response

from src.const import (
    OrderChoices,
    tteChoices,
)
from src.db import get_options_rawdata_db
from src.users import (
    User,
    get_current_active_user,
)
from src.utils import (
    eod_ini_logic_new,
    guess_exchange_and_ust,
)

router = APIRouter()


@router.get(
    '/route/to/resources',
    summary='summary of operation',
    operation_id='unique_operation_id_matching_function_name',
)
async def unique_operation_id(
        symbol: str,
        ust: str = None,
        exchange: str = None,
        tte: tteChoices = tteChoices._1m,
        startdate: Date = None,
        enddate: str = None,
        dminus: int = 30,
        order: OrderChoices = OrderChoices._asc,
        con: Connection = Depends(get_options_rawdata_db),
        user: User = Depends(get_current_active_user),
):
    """ a nice docstrings """
    args = {
        'symbol': symbol,
        'ust': ust,
        'exchange': exchange,
        'tte': tte.value,
        'startdate': startdate,
        'enddate': enddate,
        'dminus': dminus,
        'order': order.value,
    }
    content = await resolver_containing_crud_things(args, con)
    return Response(
        content=content,
        media_type='application/json')


async def select_resolve(args: t.Dict[str, t.Any]):
    args = eod_ini_logic_new(args)
    args = guess_exchange_and_ust(args)
    sql = f'''
    WITH data AS (
        SELECT 1
        {args['contn']}
    )
    SELECT json_agg(data) FROM data;
    '''
    return sql


async def resolver_containing_crud_things(args: t.Dict[str, t.Any], con: Connection):
    sql = await select_resolve(args, )
    data = await con.fetch_all(sql)
    return data
