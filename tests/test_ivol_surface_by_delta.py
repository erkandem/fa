# from src.surfacebydelta import prepare_surface_sql_arguments
import asyncio
from src.ivol_surface_by_delta import prepare_surface_sql_arguments
from src.ivol_surface_by_delta import resolve_last_date
from falib.contract import Contract
from datetime import datetime as dt


def test_sql_generation():
    args = {
        'symbol': 'cl',
        'exchange': 'cme',
        'ust': 'fut',
        'date': '2019-05-09'
    }
    sql = asyncio.run(prepare_surface_sql_arguments(args))
    assert type(sql) is str


def not_test_resolve_last_date():
    """ can't run it because a separate database engine needs to scripted first"""
    c = Contract()
    c.symbol = 'spy'
    c.exchange = 'usetf'
    c.security_type = 'eqt'
    c.target_table_name_base = c.compose_ivol_table_name_base()
    result = asyncio.run(resolve_last_date(c))
    dt.strptime(result, '%Y-%m-%d')
