import asyncio
from src.ivol_calendar_spread import select_calendar_spread


def test_sql_generation():
    args = {
        'symbol': 'spy',
        'exchange': 'usetf',
        'ust': 'eqt',
        'dminus': 30,
        'tte1': '1m',
        'tte2': '2m',
        'delta1': 'd050',
        'delta2': 'd050',
        'order': 'asc'
    }
    sql = asyncio.run(select_calendar_spread(args))
    assert type(sql) is str
