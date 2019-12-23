import asyncio
from src.ivol_smile import select_ivol_fitted_smile


def test_sql_generation():
    args = {
        'symbol': 'cl',
        'exchange': 'cme',
        'ust': 'fut',
        'startdate': '20190509',
        'enddate': '20190601',
        'tte': '1m'
    }
    sql = asyncio.run(select_ivol_fitted_smile(args))
    assert type(sql) is str
