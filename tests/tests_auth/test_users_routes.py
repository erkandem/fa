import asyncio
import json
import os
import pytest
import uuid
from starlette.testclient import TestClient
from starlette.status import HTTP_201_CREATED
from starlette.status import HTTP_200_OK
from starlette.status import HTTP_410_GONE

from app import app
import testing_utilities as tu
from src.users.auth import get_pwd_hash
from src.users.auth import get_salt
from src.users.db import delete_user_by_username
from src.users.users import create_initial_superuser
from src.users.user_models import RegisterPy
from src.users.user_models import UserPy

client = TestClient(app)

username = 'superuser'
su_data = tu.test_users[username]
su = UserPy(**su_data)
new_user_data = {
    'uid': str(uuid.uuid4()),
    'username': 'beavis',
    'salt': get_salt(),
    'hashed_salted_pwd': '',
    'email': 'beavis@test.com',
    'is_active': True,
    'roles': 'user'
}
new_user_data['hashed_salted_pwd'] = get_pwd_hash(tu.test_users_pwd, new_user_data['salt'])
new_user = UserPy(**new_user_data)


class TestInitialSuperuser:
    def test_creation_initial(self):
        data_str = os.getenv("DEFAULT_API_SUPER_USER")
        data = json.loads(data_str)
        default_su = RegisterPy(**data)
        asyncio.run(delete_user_by_username(default_su.username))
        asyncio.run(create_initial_superuser())

    def test_creation(self):
        asyncio.run(create_initial_superuser())


class TestUserRoutes:

    @classmethod
    def setup_class(cls):
        asyncio.run(tu.add_test_users_to_db())
        asyncio.run(delete_user_by_username(new_user.username))

    @classmethod
    def teardown_class(cls):
        asyncio.run(tu.delete_test_users_from_db())

    def test_get_all_users(self):
        auth_headers = tu.get_auth_header(username, client)
        response = client.get('/users', headers=auth_headers)
        assert response.status_code == HTTP_200_OK

    def test_create_new_user(self):
        auth_headers = tu.get_auth_header(username, client)
        body = {'username': new_user.username, 'password': tu.test_users_pwd}
        response = client.post('/users', json=body, headers=auth_headers)
        assert response.status_code == HTTP_201_CREATED

    def test_create_already_existing_user(self):
        auth_headers = tu.get_auth_header(username, client)
        body = {'username': new_user.username, 'password': tu.test_users_pwd}
        response = client.post('/users', json=body, headers=auth_headers)
        assert response.status_code == HTTP_200_OK

    def test_login_of_new_user(self):
        body = {'username': new_user.username, 'password': tu.test_users_pwd}
        response = client.post('/login', data=body)
        assert response.status_code == HTTP_200_OK

    def test_add_new_role(self):
        auth_headers = tu.get_auth_header(username, client)
        new_role = 'trial'
        uri = f'/users/{new_user.username}/roles/{new_role}'
        response = client.put(uri, headers=auth_headers)
        assert response.status_code == HTTP_201_CREATED

    def test_add_already_existing_role(self):
        auth_headers = tu.get_auth_header(username, client)
        new_role = 'trial'
        uri = f'/users/{new_user.username}/roles/{new_role}'
        response = client.put(uri, headers=auth_headers)
        assert response.status_code == HTTP_200_OK

    def test_delete_role(self):
        auth_headers = tu.get_auth_header(username, client)
        new_role = 'trial'
        uri = f'/users/{new_user.username}/roles/{new_role}'
        response = client.delete(uri, headers=auth_headers)
        assert response.status_code == HTTP_200_OK

    def test_change_pw(self):
        auth_headers = tu.get_auth_header(username, client)
        uri = f'/users/{new_user.username}/pw'
        body = {'username': new_user.username, 'password': tu.test_users_pwd, 'new_password': 'safepw'}
        response = client.put(uri, json=body, headers=auth_headers)
        assert response.status_code == HTTP_200_OK

    def test_delete_user(self):
        auth_headers = tu.get_auth_header(username, client)
        uri = f'/users/{new_user.username}'
        response = client.delete(uri, headers=auth_headers)
        assert response.status_code == HTTP_200_OK

