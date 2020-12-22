"""


``scopes``:
    function: the default scope, the fixture is destroyed at the end of the test.
    class: the fixture is destroyed during teardown of the last test in the class.
    module: the fixture is destroyed during teardown of the last test in the module.
    package: the fixture is destroyed during teardown of the last test in the package.
    session: the fixture is destroyed at the end of the test session.

ref: https://docs.pytest.org/en/stable/fixture.html#fixture-scopes


only tests need to be marked with ``@pytest.mark.asyncio``

https://stackoverflow.com/a/49940520/10124294
"""

import pytest
import asyncpg
import appconfig

test_users_pwd = 'secret'


@pytest.fixture(scope='function')
async def some_fixture():
    return 'input_str'


@pytest.fixture(scope='function')
async def options_db():
    db_connection = await asyncpg.pool.create_pool(
        appconfig.data_pgc.get_uri(
            appconfig.data_pgc.options_db_name
        )
    )
    return db_connection


@pytest.fixture(scope='function')
async def volatility_db():
    db_connection = await asyncpg.pool.create_pool(
        appconfig.data_pgc.get_uri(
            appconfig.data_pgc.volatility_db_name
        )
    )
    return db_connection


@pytest.fixture(scope='function')
async def prices_intraday_db():
    db_connection = await asyncpg.pool.create_pool(
        appconfig.data_pgc.get_uri(
            appconfig.data_pgc.prices_intraday_db_name
        )
    )
    return db_connection

