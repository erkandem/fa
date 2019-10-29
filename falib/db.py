from databases import Database
import asyncpg


class PostgresConfig:
    def __init__(self):
        self.user = 'postgres'
        self.pw = 'postgres'
        self.host = 'localhost'
        self.port = '5432'
        self.driver = 'psycopg2'
        self.db = 'postgresql'

    def get_uri(self, db_name):
        uri = f"{self.db}://{self.user}:{self.pw}@{self.host}:{self.port}/{db_name}"
        print(uri)
        return uri


pgc = PostgresConfig()
engines = {
    'prices': None,
    'dev': None
}
