import sqlalchemy as sa
from src.db import engines
from src.users.user_models import UserPy


metadata = sa.MetaData()
users_table = sa.Table(
    'users',
    metadata,
    sa.Column('uid', sa.String, primary_key=True, index=True),
    sa.Column('username', sa.String, unique=True),
    sa.Column('email', sa.String, unique=True),
    sa.Column('salt', sa.String),
    sa.Column('hashed_salted_pwd', sa.String),
    sa.Column('is_active', sa.Boolean, default=True),
    sa.Column('roles', sa.String, default='user')
)


def table_creation(uri: str):
    engine = sa.create_engine(uri)
    metadata.create_all(engine)
    engine.dispose()


async def user_exists_by_username(username):
    values = {'username': username}
    query = f'SELECT EXISTS (SELECT 1 FROM users WHERE username = :username);'
    row = await engines['users'].fetch_all(query, values=values)
    result = list(dict(row[0]).values())[0]
    if type(result) is int:
        result = bool(result)
    return result


async def user_isactive_by_username(username: str) -> bool:
    values = {'username': username}
    query = f'SELECT is_active FROM users WHERE username = :username;'
    row = await engines['users'].fetch_all(query, values=values)
    result = list(dict(row[0]).values())[0]
    if type(result) is int:
        result = bool(result)
    return result


async def user_pwd_by_username(username: str) -> str:
    values = {'username': username}
    query = f'SELECT hashed_salted_pwd FROM users WHERE username = :username;'
    row = await engines['users'].fetch_all(query, values=values)
    return row[0][0]


async def delete_user_by_username(username: str) -> bool:
    values = {'username': username}
    query = f'DELETE FROM users WHERE username = :username;'
    await engines['users'].execute(query, values=values)
    result = not await user_exists_by_username(username)
    return result


async def insert_new_user(user: UserPy) -> bool:
    values = user.dict()
    query = users_table.insert()
    result = await user_exists_by_username(user.username)
    if not result:
        await engines['users'].execute(query, values=values)
    result = await user_exists_by_username(user.username)
    return result


async def get_roles_by_username(username: str) -> [str]:
    values = {'username': username}
    query = f'SELECT roles FROM users WHERE username = :username;'
    result = await engines['users'].fetch_all(query, values=values)
    roles_list = result[0][0].split(',')
    return roles_list


async def update_role_by_username(username: str, roles: [str]) -> bool:
    values = {'username': username, 'roles': ','.join(roles)}
    query = f'UPDATE users SET roles = :roles WHERE username = :username;'
    await engines['users'].execute(query, values=values)
    roles_in_db = await get_roles_by_username(username)
    result = False
    if set(roles_in_db) == set(roles):
        result = True
    return result


async def update_isactive_by_username(username: str, is_active: bool) -> bool:
    values = {'username': username, 'is_active': is_active}
    query = f'UPDATE users SET is_active = :is_active WHERE username = :username;'
    await engines['users'].execute(query, values=values)
    result = await user_isactive_by_username(username)
    return result == is_active


async def update_password_by_username(username: str, salt: str, hashed_salted_pwd: str) -> bool:
    values = {'username': username, 'salt': salt, 'hashed_salted_pwd': hashed_salted_pwd}
    query = f'UPDATE users SET salt = :salt, hashed_salted_pwd = :hashed_salted_pwd WHERE username = :username;'
    await engines['users'].execute(query, values=values)
    in_db_pwd = await user_pwd_by_username(username)
    return in_db_pwd == hashed_salted_pwd


async def get_user_by_username(username: str) -> [sa.engine.RowProxy]:
    values = {'username': username}
    query = f'SELECT * FROM users WHERE username = :username LIMIT 1;'
    data = await engines['users'].fetch_all(query, values=values)
    return data


async def get_all_usernames() -> [sa.engine.RowProxy]:
    data = await engines['users'].fetch_all(f'SELECT username FROM users;')
    return data


async def get_user_obj_by_username(username: str) -> UserPy:
    data = await get_user_by_username(username)
    if len(data) > 0:
        user_dict = dict(data[0])
        return UserPy(**user_dict)
