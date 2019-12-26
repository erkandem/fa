import asyncio
import pytest
import random
from src import const
from src import intraday_prices as tm


def test_select_prices_intraday():
    args = {
        'symbol': 'spy',
        'month': None,
        'year': None,
        'ust': None,
        'exchange': None,
        'startdate': None,
        'enddate': None,
        'dminus': 30,
        'interval': 1,
        'iunit': 'month',
        'order': 'desc',
        'limit': 365
    }
    sql = asyncio.run(tm.select_prices_intraday(args))
    assert type(sql) is str
