import asyncio
import pytest
import databases

from appconfig import USERDB_URL

from src.db import engines
from src.users import db
from src.users.db import table_creation
from testing_utilities import add_test_users_to_db
from testing_utilities import delete_test_users_from_db


@pytest.mark.first
def test_add():
    table_creation(USERDB_URL)
    engines['users'] = databases.Database(USERDB_URL)
    asyncio.run(engines['users'].connect())
    db.user_db = engines['users']
    asyncio.run(add_test_users_to_db())


@pytest.mark.last
def test_remove():
    asyncio.run(delete_test_users_from_db())
