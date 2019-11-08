from src.users.db import table_creation
from src.users.db import user_exists_by_username
from src.users.db import delete_user_by_username
from src.users.db import insert_new_user
from src.users.db import get_roles_by_username
from src.users.db import update_role_by_username
from src.users.db import update_password_by_username
from src.users.db import get_user_by_username
from src.users.db import user_isactive_by_username
from src.users.db import user_pwd_by_username
from src.users.db import update_isactive_by_username
from src.users.db import get_user_obj_by_username
from src.users.users import create_initial_superuser
from appconfig import USERDB_URL

from src.users.user_models import UserPy

import asyncio
import testing_utilities as tu


def test_create_initial_superuser():
    table_creation(USERDB_URL)


class TestOperations:
    @classmethod
    def setup_class(cls):
        asyncio.run(tu.add_test_users_to_db())

    @classmethod
    def teardown_class(cls):
        asyncio.run(tu.delete_test_users_from_db())

    def test_user_exists_by_username(self):
        username = 'simple-active'
        test_result = asyncio.run(user_exists_by_username(username))
        assert test_result

    def test_delete_user_by_username(self):
        username = 'simple-active'
        user = UserPy(**tu.test_users[username])
        before = asyncio.run(user_exists_by_username(username))
        after = asyncio.run(delete_user_by_username(username))
        post_test = asyncio.run(insert_new_user(user))
        assert before
        assert after
        assert post_test

    def test_user_isactive_by_username(self):
        username = 'simple-active'
        test_result = asyncio.run(user_isactive_by_username(username))
        assert test_result == tu.test_users[username]['is_active']

    def test_user_pwd_by_username(self):
        username = 'simple-active'
        test_result = asyncio.run(user_pwd_by_username(username))
        assert test_result == tu.test_users[username]['hashed_salted_pwd']

    def test_insert_new_user(self):
        username = 'simple-active'
        user = UserPy(**tu.test_users[username])
        before = asyncio.run(delete_user_by_username(username))
        after = asyncio.run(insert_new_user(user))
        post_test = asyncio.run(user_exists_by_username(username))
        assert before
        assert after
        assert post_test

    def test_insert_new_user_caught(self):
        username = 'simple-active'
        user = UserPy(**tu.test_users[username])
        before = asyncio.run(user_exists_by_username(username))
        after = asyncio.run(insert_new_user(user))
        post_test = asyncio.run(user_exists_by_username(username))
        assert before
        assert after
        assert post_test

    def test_get_roles_by_username(self):
        username = 'simple-active'
        roles = tu.test_users[username]['roles'].split(',')
        test_result = asyncio.run(get_roles_by_username(username))
        assert test_result == roles

    def test_update_role_by_username(self):
        username = 'simple-active'
        user = UserPy(**tu.test_users[username])
        roles = tu.test_users[username]['roles'].split(',')
        new_roles = roles + ['oinkoink']
        before = asyncio.run(get_roles_by_username(username))
        upgrade = asyncio.run(update_role_by_username(username, new_roles))
        mid_test = asyncio.run(get_roles_by_username(username))
        downgrade = asyncio.run(update_role_by_username(username, roles))
        post_test = asyncio.run(get_roles_by_username(username))
        assert upgrade and downgrade
        assert set(before) == set(post_test)
        assert set(mid_test) == set(new_roles)

    def test_update_isactive_by_username(self):
        username = 'simple-inactive'
        before = asyncio.run(user_isactive_by_username(username))
        worked1 = asyncio.run(update_isactive_by_username(username, True))
        after = asyncio.run(user_isactive_by_username(username))
        worked2 = asyncio.run(update_isactive_by_username(username, False))
        assert worked1 and worked2
        assert after and not before

    def test_update_password_by_username(self):
        username = 'trial'
        pwd = tu.test_users[username]['hashed_salted_pwd']
        salt = 'salt'
        new_pw = 'hashed_salted_pw'
        pwd_in_db = asyncio.run(user_pwd_by_username(username))
        worked1 = asyncio.run(update_password_by_username(username, salt, new_pw))
        result = asyncio.run(user_pwd_by_username(username))
        assert worked1
        assert pwd_in_db == pwd
        assert result == new_pw

    def test_get_user_by_username(self):
        username = 'superuser'
        user_dict = tu.test_users[username]
        user_in_db = asyncio.run(get_user_by_username(username))
        assert user_dict == dict(user_in_db[0])

    def test_get_user_obj_by_username(self):
        username = 'superuser'
        user = UserPy(**tu.test_users[username])
        user_in_db = asyncio.run(get_user_obj_by_username(username))
        assert user == user_in_db

    def test_get_user_obj_by_username_return_none(self):
        username = 'definatly-not-a-usual-username-.-really'
        user_in_db = asyncio.run(get_user_obj_by_username(username))
        assert user_in_db is None


