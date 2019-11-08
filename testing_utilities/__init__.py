import uuid
import databases
from src.users.auth import get_salt
from src.users.auth import get_pwd_hash
from src.users.db import insert_new_user
from src.users.db import delete_user_by_username
from src.users.user_models import UserPy
import asyncio

test_users_pwd = 'secret'


def generate_test_users():
    local_test_users = {
        'trial': {
            'uid': str(uuid.uuid4()),
            'username': 'trial',
            'salt': get_salt(),
            'hashed_salted_pwd': '',
            'email': 'trial@test.com',
            'is_active': True,
            'roles': 'trial'
        },
        'simple-active': {
            'uid': str(uuid.uuid4()),
            'username': 'simple-active',
            'salt': get_salt(),
            'hashed_salted_pwd': '',
            'email': 'simple_activ@test.com',
            'is_active': True,
            'roles': 'user'
        },
        'simple-inactive': {
            'uid': str(uuid.uuid4()),
            'username': 'simple-inactive',
            'salt': get_salt(),
            'hashed_salted_pwd': '',
            'email': 'simple_inactiv@test.com',
            'is_active': False,
            'roles': 'user'
        },
        'superuser': {
            'uid': str(uuid.uuid4()),
            'username': 'superuser',
            'salt': get_salt(),
            'hashed_salted_pwd': '',
            'email': 'superuser@test.com',
            'is_active': True,
            'roles': 'superuser,user'
        }
    }

    for u in list(local_test_users):
        salt = local_test_users[u]['salt']
        local_test_users[u]['hashed_salted_pwd'] = get_pwd_hash(test_users_pwd, salt)
    return local_test_users


test_users = generate_test_users()


async def add_test_users_to_db():
    for elm in test_users.values():
        user = UserPy(**elm)
        await insert_new_user(user)


async def delete_test_users_from_db():
    for username in list(test_users):
        await delete_user_by_username(username)


def get_auth_header(username, local_client):
    if username not in list(test_users):
        raise ValueError('Username not know to test database')
    body = {'username': username, 'password': test_users_pwd}
    login_response = local_client.post('/login', data=body)
    if login_response.status_code == 200:
        token = login_response.json()['access_token']
        header = {'Authorization': f'Bearer {token}'}
        return header
    else:
        print(login_response.status_code)
        print(login_response.json())
        raise ValueError