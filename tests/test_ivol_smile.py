# from src.surfacebydelta import prepare_surface_sql_arguments
import asyncio
from src.ivol_fitted_smile import select_ivol_fitted_smile


def test_sql_generation():
    args = {'startdate': '20190509', 'enddate': '20190601', 'tte': '1m', 'symbol': 'cl', 'exchange': 'cme', 'ust': 'fut'}
    sql = asyncio.run(select_ivol_fitted_smile(args))
    assert type(sql) is str
