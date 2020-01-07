import json
import os

from fastapi import Depends
from fastapi import HTTPException
from fastapi import APIRouter
from starlette.status import HTTP_200_OK
from starlette.status import HTTP_201_CREATED
from starlette.status import HTTP_400_BAD_REQUEST
from starlette.status import HTTP_401_UNAUTHORIZED
from starlette.status import HTTP_403_FORBIDDEN
from starlette.status import HTTP_410_GONE
from starlette.status import HTTP_500_INTERNAL_SERVER_ERROR
from starlette.responses import Response

from src.users.auth import get_pwd_hash
from src.users.auth import get_current_super_user
from src.users.auth import ALLOWED_ROLES
from src.users.auth import authenticate_user
from src.users.auth import get_salt
from src.users.db import insert_new_user
from src.users.db import delete_user_by_username
from src.users.db import update_role_by_username
from src.users.db import user_exists_by_username
from src.users.db import get_roles_by_username
from src.users.db import update_password_by_username
from src.users.user_models import RegisterPy
from src.users.user_models import UserPy
from src.users.user_models import UpdatePassword

router = APIRouter()


async def create_initial_superuser():
    data_str = os.getenv('DEFAULT_API_SUPER_USER')
    data = json.loads(data_str)
    new_user = RegisterPy(**data)
    exists = await user_exists_by_username(new_user.username)
    if not exists:
        salt = get_salt()
        hashed_and_salted_pwd = get_pwd_hash(new_user.password, salt)
        new_user = UserPy(
            username=new_user.username,
            salt=salt,
            hashed_salted_pwd=hashed_and_salted_pwd
        )
        new_user.roles = f"{new_user.roles},{data['roles']}"
        await insert_new_user(new_user)


async def create_other_default_users():
    data_str = os.getenv('DEFAULT_API_USERS')
    data = json.loads(data_str)
    for elm in data:
        new_user = RegisterPy(**elm)
        exists = await user_exists_by_username(new_user.username)
        if not exists:
            salt = get_salt()
            hashed_and_salted_pwd = get_pwd_hash(new_user.password, salt)
            new_user = UserPy(
                username=new_user.username,
                salt=salt,
                hashed_salted_pwd=hashed_and_salted_pwd
            )
            new_user.roles = f"{new_user.roles},{elm['roles']}"
            await insert_new_user(new_user)


@router.post(
    '/users',
    operation_id='post_add_new_api_user'
)
async def post_add_new_api_user(
        new_user: RegisterPy,
        response: Response,
        ss: UserPy = Depends(get_current_super_user)
):
    salt = get_salt()
    hashed_salted_pwd = get_pwd_hash(new_user.password, salt)
    new_user = UserPy(
        username=new_user.username,
        salt=salt,
        hashed_salted_pwd=hashed_salted_pwd
    )
    exists = await user_exists_by_username(new_user.username)
    if exists:
        response.status_code = HTTP_200_OK
        response_msg = {'msg': f'User exists already {new_user.username}'}
        return response_msg
    result = await insert_new_user(new_user)
    if result:
        response.status_code = HTTP_201_CREATED
        response_msg = {'msg': f'created {new_user.username}'}
    else:
        raise HTTPException(
            status_code=HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f'failed to create {new_user.username}'
        )
    return response_msg


@router.delete(
    '/users/{username}',
    operation_id='delete_api_user'
)
async def delete_api_user(
    username: str,
    ss: UserPy = Depends(get_current_super_user)
):
    result = await delete_user_by_username(username)
    if result:
        response = {'msg': f'removed {username}'}
    else:
        raise HTTPException(
            status_code=HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f'failed to removed {username}'
        )
    return response


@router.put(
    '/users/{username}/pw',
    operation_id='put_change_user_pw'
)
async def put_change_user_pw(
        username: str,
        pw: UpdatePassword,
        ss: UserPy = Depends(get_current_super_user)
):
    user = await authenticate_user(username, pw.password)
    if user is None:
        raise HTTPException(
            status_code=HTTP_401_UNAUTHORIZED,
            detail='User unknown or wrong password'
        )
    salt = get_salt()
    hashed_salted_pwd = get_pwd_hash(pw.new_password, salt)
    result = await update_password_by_username(user.username, salt, hashed_salted_pwd)
    if result:
        response = {'msg': f'changed pw for {username}'}
    else:
        raise HTTPException(
            status_code=HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f'failed to change pw for {username}'
        )
    return response


@router.get(
    '/users/{username}/roles',
    operation_id='get_user_roles'
)
async def get_user_roles(
        username: str,
        ss: UserPy = Depends(get_current_super_user)
):
    if not await user_exists_by_username(username):
        return HTTPException(
            status_code=HTTP_410_GONE,
            detail='User unknown'
        )
    roles = await get_roles_by_username(username)
    return {'username': username, 'roles': roles}


@router.put(
    '/users/{username}/roles/{role}',
    operation_id='put_add_user_role'
)
async def put_add_user_role(
        username: str,
        role: str,
        response: Response,
        ss: UserPy = Depends(get_current_super_user)
):
    role = role.lower()
    if not await user_exists_by_username(username):
        return HTTPException(
            status_code=HTTP_410_GONE,
            detail='User unknown'
        )
    roles_in_db = await get_roles_by_username(username)
    if role not in ALLOWED_ROLES:
        raise HTTPException(
            status_code=HTTP_400_BAD_REQUEST,
            detail='Role is not allowed'
        )
    if role in roles_in_db:
        result = {'msg': 'already present'}
    else:
        new_roles = roles_in_db + [role]
        db_result = await update_role_by_username(username, new_roles)
        if db_result:
            result = {'msg': f'updated {username} roles'}
            response.status_code = HTTP_201_CREATED
        else:
            raise HTTPException(
                status_code=HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f'failed to update {username} roles'
            )
    return result


@router.delete(
    '/users/{username}/roles/{role}',
    operation_id='delete_user_role'
)
async def delete_user_role(
            username: str,
            role: str,
            ss: UserPy = Depends(get_current_super_user)
):
    if not await user_exists_by_username(username):
        return HTTPException(
            status_code=HTTP_410_GONE,
            detail='Unknown user'
        )
    if role not in ALLOWED_ROLES:
        raise HTTPException(
            status_code=HTTP_400_BAD_REQUEST,
            detail=f'Role called `{role}` is not allowed'
        )
    roles_in_db = await get_roles_by_username(username)
    if role not in roles_in_db:
        result = {'msg': 'role was not present in the first place'}
    else:
        new_roles = [r for r in roles_in_db if r != role]
        db_result = await update_role_by_username(username, new_roles)
        if db_result:
            result = {'msg': f'deleted "{role}" role for {username}'}
        else:
            raise HTTPException(
                status_code=HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f'failed to delete "{role}" role for {username}'
            )
    return result

