from src.ivol_summary_statistics import select_statistics_single
import asyncio


def test_select_statistics_single():
    args = {
        'symbol': 'spy',
        'ust': None,
        'exchange': None,
        'tte': '1m',
        'startdate': None,
        'enddate': None,
        'dminus': 365,
        'delta': 'd050'
    }
    sql = asyncio.run(select_statistics_single(args))
    assert type(sql) is str
