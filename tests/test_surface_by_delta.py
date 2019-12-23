# from src.surfacebydelta import prepare_surface_sql_arguments
import asyncio
from src.surfacebydelta import prepare_surface_sql_arguments


def test_sql_generation():
    args = {
        'symbol': 'cl',
        'exchange': 'cme',
        'ust': 'fut',
        'date': '20190509'
    }
    sql = asyncio.run(prepare_surface_sql_arguments(args))
    assert type(sql) is str
