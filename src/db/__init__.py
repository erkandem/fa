import typing as t

from sqlalchemy.engine import Connection, ResultProxy
import appconfig
import sqlalchemy


class Engines:
    prices_intraday: sqlalchemy.engine.Engine
    pgivbase: sqlalchemy.engine.Engine
    options_rawdata: sqlalchemy.engine.Engine
    users:  sqlalchemy.engine.Engine


def engine_factory() -> Engines:
    engines_instance = Engines()
    engines_instance.prices_intraday = sqlalchemy.create_engine(
        appconfig.data_pgc.get_uri(
            appconfig.data_pgc.prices_intraday_db_name
        )
    )
    engines_instance.pgivbase = sqlalchemy.create_engine(
        appconfig.data_pgc.get_uri(
            appconfig.data_pgc.volatility_db_name
        )
    )
    engines_instance.options_rawdata = sqlalchemy.create_engine(
        appconfig.data_pgc.get_uri(
            appconfig.data_pgc.options_db_name
        )
    )
    engines_instance.users = sqlalchemy.create_engine(
        appconfig.app_pgc.get_uri(
            appconfig.app_pgc.application_db_name
        )
    )
    return engines_instance


engines = engine_factory()

def dispose_engines(engines_instance: Engines):
    """
    release the database connections
    """
    engines_instance.prices_intraday.dispose()
    engines_instance.pgivbase.dispose()
    engines_instance.options_rawdata.dispose()
    engines_instance.users.dispose()


EngineMapping = {
    appconfig.PRICES_INTRADAY_DB_NAME: engines.prices_intraday,
    appconfig.VOLATILITY_DB_NAME: engines.pgivbase,
    appconfig.OPTIONS_DB_NAME: engines.options_rawdata,
    appconfig.APPLICATION_DB_NAME: engines.users,
}


def get_prices_intraday_db():
    connection = engines.prices_intraday.connect()
    try:
        yield connection
    finally:
        connection.close()


def get_pgivbase_db():
    connection = engines.pgivbase.connect()
    try:
        yield connection
    finally:
        connection.close()


def get_options_rawdata_db():
    connection = engines.options_rawdata.connect()
    try:
        yield connection
    finally:
        connection.close()


def get_users_db():
    connection = engines.users.connect()
    try:
        yield connection
    finally:
        connection.close()


def results_proxy_to_list_of_dict(results_proxy: ResultProxy) -> t.List[t.Dict[str, t.Any]]:
    return [{k: v for k, v in row_proxy.items()} for row_proxy in results_proxy]
