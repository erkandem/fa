import asyncio
import pytest
import random
from src import const
from src import intraday_prices as tm


def get_not_valid_value(valid_integers: [int]):
    k = 0
    is_valid = True
    not_valid_int = None
    while is_valid and k < 50:
        suggestion = random.randint(0, 60)
        if suggestion in valid_integers:
            k += 1
            continue
        else:
            is_valid = False
            not_valid_int = suggestion
    if not_valid_int is None:
        raise ValueError
    return not_valid_int


class TestSelectPricesIntraday:
    def test_initial(self):
        assert True


class TestValidator:
    def test_intervals(self):
        valid_values = [1, 2, 5, 10, 15]
        not_valid_value = get_not_valid_value(valid_values)
        v = tm.Validator()
        assert all(asyncio.run(v.interval(x)) for x in valid_values)
        assert not asyncio.run(v.interval(not_valid_value))


class TestOrder:
    def test_order_asc(self):
        v = tm.Validator()
        assert asyncio.run(v.order('asc'))
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
    test_args: tm.IntradayPricesParams

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
