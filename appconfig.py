import pathlib
import os
from enum import Enum

import dotenv
from logging import getLogger

logger = getLogger()

# mark the application folder for convenience
TOP_LEVEL_MARKER = pathlib.Path(os.path.abspath(__file__)).parent

# declare location .env file
ENV_PATH = f'{str(TOP_LEVEL_MARKER)}/.env'

# load .env which may hold value used to compose other configuration values
dotenv.load_dotenv(ENV_PATH)

#
TESTING_DB_SUFFIX = 'testing'


def evaL_bool_env(bool_env: str):
    return {
        't': True,
        'true': True,
        'f': False,
        'false': False,
    }.get(
        bool_env.lower()
    )


class PostgresConfig:
    def __init__(
            self,
            *,
            user=None,
            pw=None,
            host=None,
            port=None,
    ):
        self.user = user
        self.pw = pw
        self.host = host
        self.port = port
        self.db = 'postgresql'

    def get_uri(self, db_name):
        uri = f"{self.db}://{self.user}:{self.pw}@{self.host}:{self.port}/{db_name}"
        print(f"{self.db}://{self.user}:******@{self.host}:{self.port}/{db_name}")
        return uri

    def get_db_name(self, db_name: str):
        """
        Wrapper to get the testing or "prod" database
        depends on  testing environment variable

        Args:
            db_name (str):

        Returns:

        """
        return (
            db_name
            if not IVOLAPI_TESTING
            else ''.join([db_name, '_', TESTING_DB_SUFFIX])
        )



# application database (users) etc
IVOLAPI_PG_USER = os.getenv('IVOLAPI_PG_USER')
IVOLAPI_PG_PW = os.getenv('IVOLAPI_PG_PW')
IVOLAPI_PG_HOST = os.getenv('IVOLAPI_PG_HOST')
IVOLAPI_PG_PORT = os.getenv('IVOLAPI_PG_PORT')

PRICES_INTRADAY_DB_NAME = 'prices_intraday'
VOLATILITY_DB_NAME = 'pgivbase'
OPTIONS_DB_NAME = 'options_rawdata'
APPLICATION_DB_NAME = 'fastapi_2020'


class DatabaseNames(str, Enum):
    PRICES_INTRADAY_DB_NAME = PRICES_INTRADAY_DB_NAME
    VOLATILITY_DB_NAME = VOLATILITY_DB_NAME
    OPTIONS_DB_NAME = OPTIONS_DB_NAME
    APPLICATION_DB_NAME = APPLICATION_DB_NAME


class AppPostgresConfig(PostgresConfig):
    @property
    def application_db_name(self):
        return self.get_db_name(DatabaseNames.APPLICATION_DB_NAME)


app_pgc = AppPostgresConfig(
    user=IVOLAPI_PG_USER,
    pw=IVOLAPI_PG_PW,
    host=IVOLAPI_PG_HOST,
    port=IVOLAPI_PG_PORT,
)

# implied volatility data
PG_USER = os.getenv('PG_USER')
PG_PW = os.getenv('PG_PW')
PG_HOST = os.getenv('PG_HOST')
PG_PORT = os.getenv('PG_PORT')


class DataPostgresConfig(PostgresConfig):
    @property
    def prices_intraday_db_name(self):
        return DatabaseNames.PRICES_INTRADAY_DB_NAME  # self.get_db_name(PRICES_INTRADAY_DB_NAME)

    @property
    def volatility_db_name(self):
        return DatabaseNames.VOLATILITY_DB_NAME  # self.get_db_name(VOLATILITY_DB_NAME)

    @property
    def options_db_name(self):
        return DatabaseNames.OPTIONS_DB_NAME  # self.get_db_name(OPTIONS_DB_NAME)


data_pgc = DataPostgresConfig(
    user=PG_USER,
    pw=PG_PW,
    host=PG_HOST,
    port=PG_PORT,
)

# used for hashing/encrypting/signing
API_SECRET_KEY = os.getenv('API_SECRET_KEY')

# used to encode the validity duration into a JWT after successful login
ACCESS_TOKEN_EXPIRE_MINUTES = 30

# users, eligible for a longer expiration duration
# TODO: remove with refresh logic
LONGTERM_TOKEN_GRANTEES = [
    #
    'dashapp',
]
ACCESS_TOKEN_EXPIRE_MINUTES_LONGTERM_GRANTEE = 60 * 24 * 7


IVOLAPI_DEBUG = (
    evaL_bool_env(os.getenv('IVOLAPI_DEBUG'))
    if os.getenv('IVOLAPI_DEBUG') is not None
    else False
)
IVOLAPI_TESTING = (
    evaL_bool_env(os.getenv('IVOLAPI_TESTING'))
    if os.getenv('IVOLAPI_TESTING') is not None
    else False
)
IVOLAPI_PORT = int(os.getenv('IVOLAPI_PORT'))
IVOLAPI_HOST = os.getenv('IVOLAPI_HOST')

OPENAPI_SERVERS = [
    # exposed in OpenAPI documentation
    # used to build the base url of client libraries
    {
        'url': 'http://localhost:5000',
        'description': 'dev',
    },
    {
        'url': 'https://api.volsurf.com',
        'description': 'prod',
    },

]


# a tracker string for statcounter, all vars can be safely public
# to be injected to OpenAPI UI template
string = '''
    <!-- Default Statcounter code for api.volsurf.com https://api.volsurf.com -->
        <script type="text/javascript">
            var sc_project=12144901; 
            var sc_invisible=1; 
            var sc_security="b6ffef77"; 
        </script>
        <script type="text/javascript" src="https://www.statcounter.com/counter/counter.js" async></script>
        <noscript>
            <div class="statcounter">
                <a title="Web Analytics" href="https://statcounter.com/" target="_blank">
                    <img class="statcounter" src="https://c.statcounter.com/12144901/0/b6ffef77/1/" alt="Web Analytics">
                </a>
            </div>
        </noscript>
    <!-- End of Statcounter Code -->
'''

origins = [
    # prod
    'http://api.volsurf.com',
    'https://api.volsurf.com',

    # dev
    'http://localhost',
    'https://localhost',

    'http://0.0.0.0:5000',
    'https://0.0.0.0:5000',

    'http://127.0.0.1:5000',
    'https://127.0.0.1:5000',

    'http://localhost:5000',
    'https://localhost:5000',

    # default react/node port
    'http://0.0.0.0:3000',
    'https://0.0.0.0:3000',

    'http://127.0.0.1:3000',
    'https://127.0.0.1:3000',

    'http://localhost:3000',
    'https://localhost:3000',
]