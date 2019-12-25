import asyncio
from src.ivol_atm import select_ivol


def test_dpyd_atm_dispatcher():
    args = {
        'symbol': 'spy',
        'ust': 'eqt',
        'exchange': 'usetf',
        'startdate': None,
        'enddate': None,
        'dminus': 60,
        'tte': '1m',
        'delta': 'd050',
        'order': 'asc'

    }
    sql = asyncio.run(select_ivol(args))
    assert type(sql) is str
