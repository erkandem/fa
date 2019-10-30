from pydantic import BaseModel
import random
import string

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


async def validate_user(login: auth_model_input):
    logged_in = False
    for elm in user_database:
        if elm['username'] == login.username:
            if elm['password'] == login.password:
                logged_in = True
    return logged_in


async def create_jwt_token(login: auth_model_input):
    return ''.join([random.choice(string.ascii_letters) for i in range(0, 50)])
