from datetime import datetime as dt
from src import utils
import pytest
from starlette.exceptions import HTTPException


class TestValidators:
    def test_ensure_exchange(self):
        args = {'exchange': 'some_str'}
        utils.ensure_exchange_is_set(args)

    def test_ensure_exchange_fails(self):
        with pytest.raises(ValueError):
            args = {'exchange': None}
            utils.ensure_exchange_is_set(args)

    def test_ensure_ust(self):
        args = {'ust': 'some_str'}
        utils.ensure_security_type_is_set(args)

    def test_ensure_ust_fails(self):
        with pytest.raises(ValueError):
            args = {'ust': None}
            utils.ensure_security_type_is_set(args)

    def test_ensure_both_ust_exchange(self):
        args = {'ust': 'some_str', 'exchange': 'some_str'}
        utils.ensure_ust_and_exchange_are_set(args)

    def test_ensure_ust_fails_1(self):
        args = {'ust': None, 'exchange': 'some_str'}
        with pytest.raises(ValueError):
            utils.ensure_ust_and_exchange_are_set(args)

    def test_ensure_ust_fails_2(self):
        args = {'ust': 'some_str', 'exchange': None}
        with pytest.raises(ValueError):
            utils.ensure_ust_and_exchange_are_set(args)

    def test_nothing_touched(self):
        args = {'ust': 'some_str', 'exchange': 'some_str', 'symbol': 'some_sym'}
        with pytest.raises(HTTPException):
            utils.guess_exchange_and_ust(args)


class TestEodIniLogicNew:
    def test_no_args(self):
        args = {}
        data = utils.eod_ini_logic_new(args)
        assert dt.strptime(data['startdate'], '%Y-%m-%d') <= dt.strptime(data['enddate'], '%Y-%m-%d')

    def test_only_dminus(self):
        args = {'dminus': 30}
        data = utils.eod_ini_logic_new(args)
        assert dt.strptime(data['startdate'], '%Y-%m-%d') <= dt.strptime(data['enddate'], '%Y-%m-%d')

    def test_only_startdate(self):
        args = {'startdate': dt.today().date()}
        data = utils.eod_ini_logic_new(args)
        assert dt.strptime(data['startdate'], '%Y-%m-%d') <= dt.strptime(data['enddate'], '%Y-%m-%d')

    def test_only_enddate(self):
        args = {'enddate': dt.today().date()}
        data = utils.eod_ini_logic_new(args)
        assert dt.strptime(data['startdate'], '%Y-%m-%d') <= dt.strptime(data['enddate'], '%Y-%m-%d')

    def test_only_enddate_startdate(self):
        args = {'enddate': dt.today().date(), 'startdate': dt.today().date()}
        data = utils.eod_ini_logic_new(args)
        assert dt.strptime(data['startdate'], '%Y-%m-%d') <= dt.strptime(data['enddate'], '%Y-%m-%d')

    def test_all_params(self):
        args = {'enddate': dt.today().date(), 'startdate': dt.today().date(), 'dminus': 30}
        data = utils.eod_ini_logic_new(args)
        assert dt.strptime(data['startdate'], '%Y-%m-%d') <= dt.strptime(data['enddate'], '%Y-%m-%d')

    def test_start_bigger_than_enddate(self):
        args = {'enddate': dt(2019, 5, 20).date(), 'startdate': dt(2019, 5, 30).date()}
        data = utils.eod_ini_logic_new(args)
        assert dt.strptime(data['startdate'], '%Y-%m-%d') <= dt.strptime(data['enddate'], '%Y-%m-%d')

