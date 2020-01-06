from src.ivol_inter_spread import select_inter_ivol
import asyncio


def test_select_inter_ivol():
    args = {
        'symbol1': 'spy',
        'ust1': None,
        'exchange1': None,
        'symbol2': 'ewz',
        'ust2': None,
        'exchange2': None,
        'tte': '1m',
        'delta': 'd050',
        'startdate': None,
        'enddate': None,
        'dminus': None,
        'order': 'asc'
    }
    sql = asyncio.run(select_inter_ivol(args))
    assert type(sql) is str
