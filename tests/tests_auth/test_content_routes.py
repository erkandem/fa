import pytest
from starlette.testclient import TestClient
from app import app
import testing_utilities as tu
import asyncio


mclient = TestClient(app)


class TestPublicContentRoute:
    def test_public_has_access(self):
        response = mclient.get('/content/for-everyone')
        assert response.status_code == 200


class TestOnlyUserRoute:
    @classmethod
    def setup_class(cls):
        asyncio.run(tu.add_test_users_to_db())

    @classmethod
    def teardown_class(cls):
        asyncio.run(tu.delete_test_users_from_db())

    def test_public_fails(self):
        test_response = mclient.get('/content/only-for-users')
        assert test_response.status_code == 401

    def test_user_has_access(self):
        with TestClient(app) as client:
            username = 'simple-active'
            header = tu.get_auth_header(username, client)
            test_response = client.get('/content/only-for-users', headers=header)
            assert test_response.status_code == 200


class TestOnlyActiveUserRoute:
    @classmethod
    def setup_class(cls):
        asyncio.run(tu.add_test_users_to_db())

    @classmethod
    def teardown_class(cls):
        asyncio.run(tu.delete_test_users_from_db())

    def test_public_fails(self):
        response = mclient.get('/content/only-for-active-users')
        assert response.status_code == 401

    def test_inactive_user_fails(self):
        with TestClient(app) as client:
            username = 'simple-inactive'
            header = tu.get_auth_header(username, client)
            test_response = client.get('/content/only-for-active-users', headers=header)
            assert test_response.status_code == 403

    def test_active_user_has_access(self):
        with TestClient(app) as client:
            username = 'simple-active'
            header = tu.get_auth_header(username, client)
            test_response = client.get('/content/only-for-active-users', headers=header)
            assert test_response.status_code == 200


class TestOnlySuperUserRoute:
    @classmethod
    def setup_class(cls):
        asyncio.run(tu.add_test_users_to_db())

    @classmethod
    def teardown_class(cls):
        asyncio.run(tu.delete_test_users_from_db())

    def test_public_fails(self):
        test_response = mclient.get('/content/only-for-superusers')
        assert test_response.status_code == 401

    def test_simple_active_user_fails(self):
        with TestClient(app) as client:
            username = 'simple-active'
            header = tu.get_auth_header(username, client)
            test_response = client.get('/content/only-for-superusers', headers=header)
            assert test_response.status_code == 403

    def test_simple_inactive_user_fails(self):
        with TestClient(app) as client:
            username = 'simple-inactive'
            header = tu.get_auth_header(username, client)
            test_response = client.get('/content/only-for-superusers', headers=header)
            assert test_response.status_code == 403

    def test_superuser_has_access(self):
        with TestClient(app) as client:
            username = 'superuser'
            header = tu.get_auth_header(username, client)
            test_response = client.get('/content/only-for-superusers', headers=header)
            assert test_response.status_code == 200
