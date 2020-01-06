import asyncio
from datetime import datetime as dt
from src.ivol_smile import select_ivol_fitted_smile


def test_sql_generation():
    args = {
        'symbol': 'cl',
        'exchange': 'cme',
        'ust': 'fut',
        'startdate': dt(2019, 5, 9).date(),
        'enddate': dt(2019, 6, 1).date(),
        'tte': '1m'
    }
    sql = asyncio.run(select_ivol_fitted_smile(args))
    assert type(sql) is str
