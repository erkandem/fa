import os
import asyncpg
import databases


class PostgresConfig:
    def __init__(self):
        import dotenv
        dotenv.load_dotenv('.env')
        self.user = os.getenv("PG_USER")
        self.pw = os.getenv("PG_PW")
        self.host = os.getenv("PG_HOST")
        self.port = os.getenv("PG_PORT")
        self.db = 'postgresql'

    def get_uri(self, db_name):
        uri = f"{self.db}://{self.user}:{self.pw}@{self.host}:{self.port}/{db_name}"
        return uri


pgc = PostgresConfig()
engines = {
    'prices': asyncpg.pool.Pool,
    'dev': asyncpg.pool.Pool,
    't2': asyncpg.pool.Pool,
    'yh': asyncpg.pool.Pool,
    'users': databases.Database
}
