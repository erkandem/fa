import databases
import sqlalchemy as sa
from src.users.user_models import UserPy
import asyncpg
import asyncio
RELATION = 'users'  # sqlite
users_table = None
db = {'users': asyncpg.create_pool()}


async def table_creation():
    async with db['users'].acquire() as con:
        await con.execute('''
            CREATE TABLE IF NOT EXISTS users (
                uid character varying NOT NULL,
                username character varying UNIQUE,
                email character varying UNIQUE,
                salt character varying,
                hashed_salted_pwd character varying,
                is_active boolean,
                roles character varying,
                PRIMARY KEY (uid)
            );
            ''')


async def user_exists_by_username(username):
    query = f'SELECT EXISTS (SELECT 1 FROM users WHERE username = $1);'
    async with db['users'].acquire() as con:
        row = await con.fetchval(query, username)
        return row


async def user_isactive_by_username(username: str) -> bool:
    query = f'SELECT is_active FROM users WHERE username = $1;'
    async with db['users'].acquire() as con:
        row = await con.fetch(query, username)
    return bool(row[0][0])


async def user_pwd_by_username(username: str) -> str:
    query = f'SELECT hashed_salted_pwd FROM users WHERE username = $1;'
    async with db['users'].acquire() as con:
        row = await con.fetch(query, username)
        return row


async def delete_user_by_username(username: str) -> bool:
    query = f'DELETE FROM users WHERE username = $1;'
    async with db['users'].acquire() as con:
        await con.execute(query, username)
    result = not await user_exists_by_username(username)
    return result


async def insert_new_user(u: UserPy) -> bool:
    async with db['users'].acquire() as con:
        await con.execute(
            '''INSERT INTO users (
                uid, username, email, salt, hashed_salted_pwd, is_active, roles
            ) VALUES ($1, $2, $3, $4, $5, $6, $7);''',
            u.uid, u.username, u.email, u.salt, u.hashed_salted_pwd, u.is_active, u.roles)
    result = await user_exists_by_username(u.username)
    return result


async def get_roles_by_username(username: str) -> [str]:
    query = f'SELECT roles FROM users WHERE username = $1;'
    async with db['users'].acquire() as con:
        result = await con.fetch(query, username)
    roles_list = result.split(',')
    return roles_list


async def update_role_by_username(username: str, roles: [str]) -> bool:
    query = f'UPDATE users SET roles = $2 WHERE username = $1;'
    async with db['users'].acquire() as con:
        await con.execute(query, username, ','.join(roles))
    roles_in_db = await get_roles_by_username(username)
    result = False
    if set(roles_in_db) == set(roles):
        result = True
    return result


async def update_isactive_by_username(username: str, is_active: bool) -> bool:
    async with db['users'].acquire() as con:
        await con.execute(
            'UPDATE users SET is_active = $2 WHERE username = $1;',
            username, is_active)
    result = await user_isactive_by_username(username)
    return result == is_active


async def update_password_by_username(username: str, salt: str, hashed_salted_pwd: str) -> bool:
    query = f'UPDATE users SET salt = $2, hashed_salted_pwd = $3 WHERE username = $1;'
    async with db['users'].acquire() as con:
        await con.execute(query, {username, salt, hashed_salted_pwd})
    in_db_pwd = await user_pwd_by_username(username)
    return in_db_pwd == hashed_salted_pwd


async def get_user_by_username(username: str) -> [sa.engine.RowProxy]:
    query = f'SELECT * FROM users WHERE username = $1 LIMIT 1;'
    async with db['users'].acquire() as con:
        data = await con.fetch(query, username)
    return data


async def get_user_obj_by_username(username: str) -> UserPy:
    data = await get_user_by_username(username)
    if len(data) > 0:
        user_dict = dict(data[0])
        return UserPy(**user_dict)
