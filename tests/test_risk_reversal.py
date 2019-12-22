import asyncio
from src.risk_reversal import select_risk_reversal


def test_sql_generation():
    args = {
        'symbol': 'cl',
        'dminus': 30,
        'delta1': 'd060',
        'delta2': 'd040',
        'exchange': 'usetf',
        'ust': 'eqt',
        'tte': '1m',
        'order': 'asc'
    }
    sql = asyncio.run(select_risk_reversal(args))
    assert type(sql) is str
