import psycopg2
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
        dsn_dict = PgSync.get_dsn()
        return DatabaseLink(**dsn_dict)

    @staticmethod
    def get_dsn() -> {}:
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
            dsn = PgSync.get_dsn()
        con = psycopg2.connect(dsn)
        return con

    @staticmethod
    def execute_and_fetchall(con, sql: str):
        with con.cursor() as cur:
            cur.execute(sql)
            data = cur.fetchall()
            return data

