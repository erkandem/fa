from pydantic import BaseModel
import random
import string
import fastapi

router = fastapi.APIRouter()


auth_model = {'access_token': str}
auth_model_output ={'access_token': str}
refresh_out = {'refreshed_token': str}


class auth_model_input(BaseModel):
    username: str
    password: str


class refresh_model_input(BaseModel):
    token: str


user_database = [
    {'id': 0, 'username': 'guru', 'password': 'urug'}
]
authorized_tokens = [{'id': 0, 'token': 'macceroni'}]


@router.post('/login')
async def login_route(login: auth_model_input):
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


@router.post('/refresh')
async def refresh_route(token: refresh_model_input):
    return {'refreshed_token': f'fresh_{token.token}'}


async def validate_user(login: auth_model_input):
    logged_in = False
    for elm in user_database:
        if elm['username'] == login.username:
            if elm['password'] == login.password:
                logged_in = True
    return logged_in


async def create_jwt_token(login: auth_model_input):
    return ''.join([random.choice(string.ascii_letters) for i in range(0, 50)])
