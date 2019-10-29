import os


class PostgresConfig:
    def __init__(self):
        import dotenv
        dotenv.load_dotenv('.env')
        config = os.getenv('FA_API_CONFIG')
        if config is None:
            raise ValueError
        if config == 'ubuntu':
            self.user = 'postgres'
            self.pw = 'postgres'
            self.host = 'localhost'
            self.port = '5432'
            self.db = 'postgresql'
        elif config == 'docker':
            self.user = 'docker'
            self.pw = 'docker'
            self.host = '172.17.0.1'
            self.port = '5432'
            self.db = 'postgresql'
        else:
            raise NotImplementedError

    def get_uri(self, db_name):
        uri = f"{self.db}://{self.user}:{self.pw}@{self.host}:{self.port}/{db_name}"
        print(uri)
        return uri


pgc = PostgresConfig()
engines = {
    'prices': None,
    'dev': None
}
