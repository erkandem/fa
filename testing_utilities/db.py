import psycopg2
from psycopg2.extras import RealDictCursor
from collections import namedtuple

DatabaseLink = namedtuple(
    'DatabaseLink',
    ['dialect', 'user', 'pw', 'host', 'port', 'db_name']
)


class PgSync:
    """devtool"""
    @staticmethod
    def compose_dsn(nt: DatabaseLink) -> str:
        return f'{nt.dialect}://{nt.user}:{nt.pw}@{nt.host}:{nt.port}/{nt.db_name}'

    @staticmethod
    def get_dsn_nt() -> DatabaseLink:
        dsn_dict = PgSync.get_dsn_dict()
        return DatabaseLink(**dsn_dict)

    @staticmethod
    def get_dsn_dict() -> {}:
        return dict(
            pw='postgres',
            user='postgres',
            host='localhost',
            port='5432',
            db_name='options_rawdata',
            dialect='postgresql'
        )

    @staticmethod
    def get_con(dsn: str = None):
        if dsn is None:
            dsn = PgSync.compose_dsn(PgSync.get_dsn_nt())
        con = psycopg2.connect(dsn)
        return con

    @staticmethod
    def fetch(con, sql: str):
        with con.cursor() as cur:
            cur.execute(sql)
            data = cur.fetchall()
            return data

    @staticmethod
    def fetch_with_names(con, sql: str):
        with con.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute(sql)
            data = cur.fetchall()
            return data

