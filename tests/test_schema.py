import pytest
from starlette.exceptions import HTTPException

from src.schema import (
    BaseContract,
    _validate_config,
    validate_config,
)


def test_validate_config():
    args = {'ust': 'eqt', 'exchange': 'usetf', 'symbol': 'xrt'}
    validate_config(args)


def test_validate_config_fails():
    args = {'ust': 'eqt', 'exchange': 'usetf', 'symbol': 'stop'}
    with pytest.raises(HTTPException):
        validate_config(args)


def test__validate_config():
    args = {'ust': 'eqt', 'exchange': 'usetf', 'symbol': 'xrt'}
    config = BaseContract(**args)
    assert _validate_config(config)


def test__validate_config_fails():
    args = {'ust': 'eqt', 'exchange': 'usetf', 'symbol': 'stop'}
    config = BaseContract(**args)
    assert not _validate_config(config)
