# from src.surfacebydelta import prepare_surface_sql_arguments
import asyncio
from src.surfacebydelta import prepare_surface_sql_arguments


def test_sql_generation():
    args = {'date': '20190509', 'symbol': 'cl', 'exchange': 'cme', 'ust': 'fut'}
    sql = asyncio.run(prepare_surface_sql_arguments(args))
    assert type(sql) is str
