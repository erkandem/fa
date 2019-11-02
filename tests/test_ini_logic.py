"""

"""
from datetime import datetime as dt
from src.utils import eod_ini_logic
import asyncio


def test_ini_logic():
    startdate = '20190905'
    args = {
        'symbol': 'ewz', 'month': 'f', 'year': 2019, 'ust': 'eqt', 'exchange': 'usetf',
        'startdate': startdate, 'enddate': '20191005', 'dminus': 20, 'order': 'asc'
    }
    result = asyncio.run(eod_ini_logic(args))
    check_me = dt.strptime(result['startdate'], '%Y-%m-%d').strftime('%Y%m%d')
    assert check_me == startdate


def test_ini_logic_2():
    startdate = None
    args = {
        'symbol': 'ewz', 'month': 'f', 'year': 2019, 'ust': 'eqt', 'exchange': 'usetf',
        'startdate': startdate, 'enddate': '20191005', 'dminus': 20, 'order': 'asc'
    }
    result = asyncio.run(eod_ini_logic(args))
    check_me = dt.strptime(result['startdate'], '%Y-%m-%d')
    assert type(check_me.strftime('%Y%m%d')) is str


def test_ini_logic_3():
    startdate = None
    enddate = None
    args = {
        'symbol': 'ewz', 'month': 'f', 'year': 2019, 'ust': 'eqt', 'exchange': 'usetf',
        'startdate': startdate, 'enddate': enddate, 'dminus': 20, 'order': 'asc'
    }
    result = asyncio.run(eod_ini_logic(args))
    check_me = dt.strptime(result['startdate'], '%Y-%m-%d')
    check_me2 = dt.strptime(result['enddate'], '%Y-%m-%d')
    assert type(check_me.strftime('%Y%m%d')) is str
    assert type(check_me2.strftime('%Y%m%d')) is str
    assert check_me2  >= check_me


def test_ini_logic_4():
    startdate = None
    enddate = '20190519'
    args = {
        'symbol': 'ewz', 'month': 'f', 'year': 2019, 'ust': 'eqt', 'exchange': 'usetf',
        'startdate': startdate, 'enddate': enddate, 'dminus': 20, 'order': 'asc'
    }
    result = asyncio.run(eod_ini_logic(args))
    check_me = dt.strptime(result['startdate'], '%Y-%m-%d')
    check_me2 = dt.strptime(result['enddate'], '%Y-%m-%d')
    assert type(check_me.strftime('%Y%m%d')) is str
    assert type(check_me2.strftime('%Y%m%d')) is str
    assert check_me2  >= check_me


def test_ini_logic_5():
    startdate = '20190519'
    enddate = '20190519'
    args = {
        'symbol': 'ewz', 'month': 'f', 'year': 2019, 'ust': 'eqt', 'exchange': 'usetf',
        'startdate': startdate, 'enddate': enddate, 'dminus': 20, 'order': 'asc'
    }
    result = asyncio.run(eod_ini_logic(args))
    check_me = dt.strptime(result['startdate'], '%Y-%m-%d')
    check_me2 = dt.strptime(result['enddate'], '%Y-%m-%d')
    assert type(check_me.strftime('%Y%m%d')) is str
    assert type(check_me2.strftime('%Y%m%d')) is str
    assert check_me2 >= check_me


def test_ini_logic_6():
    startdate = '20190520'
    enddate = '20190519'
    args = {
        'symbol': 'ewz', 'month': 'f', 'year': 2019, 'ust': 'eqt', 'exchange': 'usetf',
        'startdate': startdate, 'enddate': enddate, 'dminus': 20, 'order': 'asc'
    }
    result = asyncio.run(eod_ini_logic(args))
    check_me = dt.strptime(result['startdate'], '%Y-%m-%d')
    check_me2 = dt.strptime(result['enddate'], '%Y-%m-%d')
    assert type(check_me.strftime('%Y%m%d')) is str
    assert type(check_me2.strftime('%Y%m%d')) is str
    assert check_me2 >= check_me


def test_ini_logic_7():
    startdate = '20190520'
    enddate = '20190519'
    args = {
        'symbol': 'ewz', 'month': 'f', 'year': 2019, 'ust': 'eqt', 'exchange': 'usetf',
        'startdate': startdate, 'enddate': enddate, 'dminus': None, 'order': 'asc'
    }
    result = asyncio.run(eod_ini_logic(args))
    assert type(result['dminus']) is int
