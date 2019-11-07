from pydantic import BaseModel
import random
import string
import fastapi

router = fastapi.APIRouter()

auth_model = {'access_token': str}
auth_model_output = {'access_token': str}
refresh_out = {'refreshed_token': str}


class auth_model_input(BaseModel):
    username: str
    password: str


async def create_jwt_token(login: auth_model_input):
    return ''.join([random.choice(string.ascii_letters) for i in range(0, 50)])


async def decode_jwt_token():
    return 'some_info'


class refresh_model_input(BaseModel):
    token: str


user_database = [{'id': 0, 'username': 'guru', 'password': 'urug'}]
authorized_tokens = [{'id': 0, 'token': 'macaroni'}]


@router.post('/login', operation_id='post_api_login_endpoint', tags=['Auth'])
async def post_api_login_endpoint(login: auth_model_input):
    """
    [fastapi security](https://fastapi.tiangolo.com/tutorial/security/oauth2-jwt/)

    [user management](https://frankie567.github.io/fastapi-users/)

    [user management example](https://frankie567.github.io/fastapi-users/configuration/full_example/)

    """
    if validate_user(login):
        token = await create_jwt_token(login)
        return {'access_token': f'{token}'}
    else:
        return {'error': 'login failed'}


@router.post('/refresh', operation_id='post_api_refresh_token', tags=['Auth'])
async def post_api_refresh_token(token: refresh_model_input):
    return {'refreshed_token': f'fresh_{token.token}'}


async def validate_user(login: auth_model_input):
    logged_in = False
    for elm in user_database:
        if elm['username'] == login.username:
            if elm['password'] == login.password:
                logged_in = True
    return logged_in
