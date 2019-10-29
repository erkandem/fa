from databases import Database


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


price_engine = Database(PostgresConfig().get_uri('prices_intraday'))
dev_engine = Database(PostgresConfig().get_uri('pymarkets_null'))

