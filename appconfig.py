import pathlib
import os
import dotenv

# mark the application folder for convenience
TOP_LEVEL_MARKER = pathlib.Path(os.path.abspath(__file__)).parent

# declare location .env file
ENV_PATH = f'{str(TOP_LEVEL_MARKER)}/.env'

# load .env which may hold value used to compose other configuration values
dotenv.load_dotenv(ENV_PATH)

# compose or read in the database_url
USERDB_URL = f'sqlite:////{str(TOP_LEVEL_MARKER)}/db.sqlite'
USERDB_URL_PG_TESTS = f'postgresql://postgres:postgres@localhost:5432/fastapi_tests'

# used for hashing/encrypting/signing
API_SECRET_KEY = os.getenv('API_SECRET_KEY')

# algo used to hash the password
API_HASH_ALGORITHM = "HS256"

# API_SECRET_KEY = os.getenv('API_HASH_ALGORITHM')

# used to encode the validity duration into a JWT after successful login
ACCESS_TOKEN_EXPIRE_MINUTES = 30

# users, eligible for a longer expiration duration
# TODO: remove with refresh logic
LONGTERM_TOKEN_GRANTEES = [
    #
    'dashapp',
]
ACCESS_TOKEN_EXPIRE_MINUTES_LONGTERM_GRANTEE = 60 * 24 * 7


def evaL_bool_env(bool_env: str):
    return {
        't': True,
        'true': True,
        'f': False,
        'false': False,
    }.get(
        bool_env.lower()
    )


DEBUG = (
    evaL_bool_env(os.getenv('DEBUG'))
    if os.getenv('DEBUG') is not None
    else False
)
FASTAPI_PORT = os.getenv('FASTAPI_PORT')
FASTAPI_HOST = os.getenv('FASTAPI_HOST')

OPENAPI_SERVERS = [
    # exposed in OpenAPI documentation
    # used to bult the base url of client libraries
    {
        'url': 'https://api.volsurf.com',
        'description': 'prod',
    },
    {
        'url': 'http://localhost:5000',
        'description': 'dev',
    }
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
