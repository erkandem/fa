import pytest
from starlette.testclient import TestClient
from app import app
import testing_utilities as tu
import asyncio

client = TestClient(app)


class TestDecoratedRoutes:
    @classmethod
    def setup_class(cls):
        asyncio.run(tu.add_test_users_to_db())

    @classmethod
    def teardown_class(cls):
        asyncio.run(tu.delete_test_users_from_db())

    def test_public(self):
        test_response = client.get('/dc/for-everyone')
        assert test_response.status_code == 200

    def test_active_user_roles(self):
        username = 'simple-active'
        header = tu.get_auth_header(username, client)
        test_response = client.get('/dc/only-for-active-users', headers=header)
        assert test_response.status_code == 200

    def test_active_user_roles_fails(self):
        username = 'simple-inactive'
        header = tu.get_auth_header(username, client)
        test_response = client.get('/dc/only-for-active-users', headers=header)
        assert test_response.status_code == 403

    def test_superuser_route(self):
        username = 'superuser'
        header = tu.get_auth_header(username, client)
        test_response = client.get('/dc/only-for-superusers', headers=header)
        assert test_response.status_code == 200

    def test_superuser_route_fails(self):
        username = 'simple-inactive'
        header = tu.get_auth_header(username, client)
        test_response = client.get('/dc/only-for-superusers', headers=header)
        assert test_response.status_code == 403

    def test_superuser_route_fails_2(self):
        username = 'simple-active'
        header = tu.get_auth_header(username, client)
        test_response = client.get('/dc/only-for-superusers', headers=header)
        assert test_response.status_code == 403

    def test_accepted_decorator_user(self):
        username = 'simple-active'
        header = tu.get_auth_header(username, client)
        test_response = client.get('/dc/only-for-active-superusers-and-active-users', headers=header)
        assert test_response.status_code == 200

    def test_accepted_roles_decorator_superuser(self):
        username = 'superuser'
        header = tu.get_auth_header(username, client)
        test_response = client.get('/dc/only-for-active-superusers-and-active-users', headers=header)
        assert test_response.status_code == 200

    def test_accepted_roles_decorator_simple_inactive(self):
        username = 'simple-inactive'
        header = tu.get_auth_header(username, client)
        test_response = client.get('/dc/only-for-active-superusers-and-active-users', headers=header)
        assert test_response.status_code == 403

    def test_accepted_roles_decorator_trial(self):
        username = 'trial'
        header = tu.get_auth_header(username, client)
        test_response = client.get('/dc/only-for-active-superusers-and-active-users', headers=header)
        assert test_response.status_code == 403

