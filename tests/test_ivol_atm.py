import asyncio
from src.ivol_atm import dpyd_atm_dispatcher


def test_dpyd_atm_dispatcher():
    args = {
        'symbol': 'spy',
        'ust': 'eqt',
        'exchange': 'usetf',
        'tte': '1m',
        'startdate': None,
        'enddate': None,
        'dminus': 60,
        'order': 'asc'
    }
    sql = asyncio.run(dpyd_atm_dispatcher(args))
    assert type(sql) is str
