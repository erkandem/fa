import random

import pytest

from src import const


def test_const_metric_mapper():
    metric = random.choice(list(const.RAWOPTION_MAP))
    result = const.metric_mapper_f(metric)
    assert result == const.RAWOPTION_MAP[metric]


def test_const_metric_mapper_not_found():
    metric = 'wtf'
    result = const.metric_mapper_f(metric)
    assert result == 'undprice'


def test_time_to_var_func():
    test_value = random.choice(list(const.time_to_var))
    result = const.time_to_var_func(test_value)
    assert result == const.time_to_var[test_value]


def test_time_to_var_func_fails():
    with pytest.raises(KeyError):
        test_value = 'wtf'
        const.time_to_var_func(test_value)
