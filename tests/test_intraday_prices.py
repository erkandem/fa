'''
args = {
    'symbol': symbol, 'month': month, 'year': year, 'ust': ust, 'exchange': exchange,
    'startdate': startdate, 'enddate': enddate, 'dminus': dminus,
    'interval': interval, 'iunit': iunit, 'order': order.value
}
'''

import asyncio
import pytest
import random
from falib import const
from src import intraday_prices as tm


class TestSelectPricesIntraday:
    def test_initial(self):
        assert True


class TestValidator:
    def test_interval_1(self):
        v = tm.Validator()
        assert asyncio.run(v.interval(1))

    def test_interval_2(self):
        v = tm.Validator()
        assert asyncio.run(v.interval(2))

    def test_interval_5(self):
        v = tm.Validator()
        assert asyncio.run(v.interval(5))

    def test_interval_10(self):
        v = tm.Validator()
        assert asyncio.run(v.interval(10))

    def test_interval_15(self):
        v = tm.Validator()
        assert asyncio.run(v.interval(15))


class TestOrder:
    def test_order_asc(self):
        v = tm.Validator()
        assert asyncio.run(v.order('asc'))

    def test_order_desc(self):
        v = tm.Validator()
        assert asyncio.run(v.order('desc'))


class TestSymbol:
    def test_symbol(self):
        v = tm.Validator()
        test_sym = random.choice(const.prices_intraday_all_symbols)
        assert asyncio.run(v.symbols(test_sym))

    def test_symbol_fails(self):
        v = tm.Validator()
        test_sym = 'nas'
        assert not asyncio.run(v.symbols(random.choice(test_sym)))


class TestMonth:
    def test_month(self):
        v = tm.Validator()
        test_char = random.choice(const.futures_month_chars)
        assert asyncio.run(v.month(test_char))

    def test_month_fails_1(self):
        v = tm.Validator()
        test_char = 'p'
        assert not asyncio.run(v.month(test_char))

    def test_month_fails_2(self):
        v = tm.Validator()
        test_char = '1'
        assert not asyncio.run(v.month(test_char))


class TestExchange:
    def test_exchnage(self):
        v = tm.Validator()
        test_exchange = random.choice(const.exchange_choices_intraday)
        assert asyncio.run(v.exchange(test_exchange))

    def test_exchnage_fails(self):
        v = tm.Validator()
        test_exchange = 'sth'
        assert not asyncio.run(v.exchange(test_exchange))

class TestUst:
    def test_ust(self):
        v = tm.Validator()
        test_ust = random.choice(const.ust_choices_intraday)
        assert asyncio.run(v.ust(test_ust))

    def test_ust_fails(self):
        v = tm.Validator()
        test_ust = 'sth'
        assert not asyncio.run(v.ust(test_ust))


class TestSqlCasting:
    def setup(self):
        test_args = {key: 'test' for key in tm.IntradayPricesParams._fields}
        self.test_args = tm.IntradayPricesParams(**test_args)

    def test_casting_logic(self):
        asyncio.run(tm._cast_to_sql(self.test_args, sc_flag=False))

    def test_casting_logic_2(self):
        asyncio.run(tm._cast_to_sql(self.test_args, sc_flag=True))

    def test_cast_to_sql_a(self):
        asyncio.run(tm._cast_to_sql_a(self.test_args))

    def test_cast_to_sql_b(self):
        asyncio.run(tm._cast_to_sql_b(self.test_args))
