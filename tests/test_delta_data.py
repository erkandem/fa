import asyncio
from datetime import datetime as dt
from src.delta_data import delta_query_sql


def delta_query():
    """ devtool """
    args = {}
    args["symbol"] = 'cl'
    args["ust"] = 'fut'
    args["exchange"] = 'cme'
    args["underlying_month"] = '201912'
    args["option_month"] = '201912'
    args["ltd"] = '20191115'
    args['startdate'] = dt(2019, 1, 1).date().strftime('%Y-%m-%d')
    args['enddate'] = dt(2019, 4, 1).date().strftime('%Y-%m-%d')
    return args


def test_delta_query_sql():
    pass
