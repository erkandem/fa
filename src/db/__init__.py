import typing as t
import logging

from sqlalchemy.engine import ResultProxy
import sqlalchemy
from sqlalchemy.orm import sessionmaker

import appconfig


logging.getLogger(__name__)


class Engines:
    """wrapper class, could be a dict, but let's stay dot-accessible"""
    prices_intraday: sqlalchemy.engine.Engine
    pgivbase: sqlalchemy.engine.Engine
    options_rawdata: sqlalchemy.engine.Engine
    users:  sqlalchemy.engine.Engine


class SessionMakers:
    """wrapper class, could be a dict, but let's stay dot-accessible"""
    prices_intraday: sessionmaker
    pgivbase: sessionmaker
    options_rawdata: sessionmaker
    users:  sessionmaker


def engine_factory() -> Engines:
    """
    Calls ``create_engine`` for all databases needed for the app.
    Returns a dot-accessible wrapper class.
    """
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


def sessionmaker_factory(engines_instance: Engines) -> SessionMakers:
    session_makers = SessionMakers()
    session_makers.prices_intraday = sessionmaker(bind=engines_instance.prices_intraday, autocommit=True)
    session_makers.pgivbase = sessionmaker(bind=engines_instance.pgivbase, autocommit=True)
    session_makers.options_rawdata = sessionmaker(bind=engines_instance.options_rawdata, autocommit=True)
    session_makers.users = sessionmaker(bind=engines_instance.users, autocommit=True)
    return session_makers


engines = engine_factory()
sessions = sessionmaker_factory(engines)


def dispose_engines():
    """
    release the database Sessions
    """
    logging.info('Disposing database engines.')
    engines.prices_intraday.dispose()
    engines.pgivbase.dispose()
    engines.options_rawdata.dispose()
    engines.users.dispose()


def get_prices_intraday_db():
    session = sessions.prices_intraday()
    try:
        yield session
    finally:
        session.close()


def get_pgivbase_db():
    session = sessions.pgivbase()
    try:
        yield session
    finally:
        session.close()


def get_options_rawdata_db():
    session = sessions.options_rawdata()
    try:
        yield session
    finally:
        session.close()


def get_users_db():
    session = sessions.users()
    try:
        yield session
    finally:
        session.close()


def results_proxy_to_list_of_dict(results_proxy: ResultProxy) -> t.List[t.Dict[str, t.Any]]:
    """
    The default cursor in SQLAlchemy returns objects with column names.
    Here, we fetch the results such, that we preserve the column names.

    Thx https://stackoverflow.com/a/50141868/10124294
    """
    return [{k: v for k, v in row_proxy.items()} for row_proxy in results_proxy]
