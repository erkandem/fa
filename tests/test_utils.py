from src import utils
import asyncio
import pytest


class TestValidators:
    def test_ensure_exchange(self):
        args = {'exchange': 'some_str'}
        asyncio.run(utils.ensure_exchange_is_set(args))

    def test_ensure_exchange_fails(self):
        with pytest.raises(ValueError):
            args = {'exchange': None}
            asyncio.run(utils.ensure_exchange_is_set(args))

    def test_ensure_ust(self):
        args = {'ust': 'some_str'}
        asyncio.run(utils.ensure_security_type_is_set(args))

    def test_ensure_ust_fails(self):
        with pytest.raises(ValueError):
            args = {'ust': None}
            asyncio.run(utils.ensure_security_type_is_set(args))

    def test_ensure_both_ust_exchange(self):
        args = {'ust': 'some_str', 'exchange': 'some_str'}
        asyncio.run(utils.ensure_ust_and_exchange_are_set(args))

    def test_ensure_ust_fails_1(self):
        args = {'ust': None, 'exchange': 'some_str'}
        with pytest.raises(ValueError):
            asyncio.run(utils.ensure_ust_and_exchange_are_set(args))

    def test_ensure_ust_fails_2(self):
        args = {'ust': 'some_str', 'exchange': None}
        with pytest.raises(ValueError):
            asyncio.run(utils.ensure_ust_and_exchange_are_set(args))

    def test_nothing_touched(self):
        args = {'ust': 'some_str', 'exchange': 'some_str'}
        asyncio.run(utils.guess_exchange_and_ust(args))

