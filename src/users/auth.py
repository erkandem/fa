import asyncio
import functools
from datetime import datetime
from datetime import timedelta
import os
import jwt
from fastapi import Depends
from fastapi import HTTPException
from fastapi import APIRouter
from fastapi.security import OAuth2PasswordRequestForm
from fastapi.security import OAuth2PasswordBearer
from passlib.context import CryptContext
from pydantic import BaseModel
from starlette.status import HTTP_400_BAD_REQUEST
from starlette.status import HTTP_401_UNAUTHORIZED
from starlette.status import HTTP_403_FORBIDDEN

from appconfig import API_SECRET_KEY
from appconfig import API_HASH_ALGORITHM
from appconfig import ACCESS_TOKEN_EXPIRE_MINUTES

from src.users.db import user_exists_by_username
from src.users.db import get_user_obj_by_username
from src.users.user_models import UserPy

SUPERUSER = 'superuser'
USER = 'user'
TRIAL = 'trial'
ALLOWED_ROLES = [SUPERUSER, USER, TRIAL]
ACCESS_TOKEN_EXPIRES_TDT = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    username: str = None


def get_salt():
    return os.urandom(32).hex()


router = APIRouter()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl='/login')
pwd_context = CryptContext(schemes=['bcrypt'], deprecated='auto')


def salt_pwd(plain_pwd, salt):
    return f'{plain_pwd}{salt}'


def verify_plain_pwd(plain_pwd, salt, hashed_and_salted_pwd):
    salted_pwd = salt_pwd(plain_pwd, salt)
    return verify_salted_pwd(salted_pwd, hashed_and_salted_pwd)


def verify_salted_pwd(salted_pwd, hashed_and_salted_pwd):
    return pwd_context.verify(salted_pwd, hashed_and_salted_pwd)


def get_hash_of_salted_pwd(salted_pwd):
    return pwd_context.hash(salted_pwd)


def get_pwd_hash(password, salt):
    salted_pwd = salt_pwd(password, salt)
    return get_hash_of_salted_pwd(salted_pwd)


async def get_roles(current_user: UserPy):
    roles = current_user.roles.split(',')
    return roles


async def get_roles_as_set(current_user: UserPy):
    roles_set = set(n for n in await get_roles(current_user))
    return roles_set


async def authenticate_user(username: str, password: str) -> UserPy:
    if await user_exists_by_username(username):
        user = await get_user_obj_by_username(username)
        if verify_plain_pwd(password, user.salt, user.hashed_salted_pwd):
            return user


def create_access_token(*, data: dict, expires_delta: timedelta = None):
    """ encode/sign details to `subjects's` access rights and token properties"""
    to_encode = data.copy()
    now = datetime.utcnow()
    if expires_delta:
        expire = now + expires_delta
    else:
        expire = now + timedelta(minutes=15)
    to_encode.update({'exp': expire})
    encoded_jwt = jwt.encode(
        to_encode,
        API_SECRET_KEY,
        algorithm=API_HASH_ALGORITHM
    )
    return encoded_jwt


async def try_decode(token):
    try:
        payload = jwt.decode(
            token,
            API_SECRET_KEY,
            algorithms=[API_HASH_ALGORITHM]
        )
        username: str = payload.get('sub')
        if username is None:
            raise HTTPException(status_code=HTTP_401_UNAUTHORIZED, detail='Username unknown')
        token_data = TokenData(username=username)
    except jwt.PyJWTError:
        raise HTTPException(status_code=HTTP_400_BAD_REQUEST, detail='Identification failed')
    return token_data


async def get_current_user(token: str = Depends(oauth2_scheme)) -> UserPy:
    token_data = await try_decode(token)
    user = await get_user_obj_by_username(token_data.username)
    if user is None:
        raise HTTPException(status_code=HTTP_401_UNAUTHORIZED, detail='Username unknown')
    return user


async def get_current_active_user(current_user: UserPy = Depends(get_current_user)):
    if not current_user.is_active:
        raise HTTPException(
            status_code=HTTP_403_FORBIDDEN,
            detail='You are currently set as `inactive`'
        )
    return current_user


async def get_current_super_user(current_user: UserPy = Depends(get_current_user)):
    roles = await get_roles(current_user)
    if SUPERUSER not in roles:
        raise HTTPException(
            status_code=HTTP_403_FORBIDDEN,
            detail='You must be a superuser to access this endpoint'
        )
    return current_user



class bouncer:
    @staticmethod
    def roles_accepted(*roles_accepted):
        """ one or more of the required roles have to be among the granted roles """
        def decorator(f):
            @functools.wraps(f)
            def wrapper(*args, **kwargs):
                roles_accepted_set = set([str(n) for n in roles_accepted])
                roles_granted_set = asyncio.run(get_roles_as_set(kwargs['user']))
                if roles_granted_set.isdisjoint(roles_accepted_set):
                    req_str = ' ,'.join(roles_accepted_set)
                    gran_str = ' ,'.join(roles_granted_set)
                    raise HTTPException(
                        status_code=HTTP_403_FORBIDDEN,
                        detail=f'roles of ACTIVE users required: {req_str} roles granted: {gran_str}'
                    )
                return f(*args, **kwargs)
            return wrapper
        return decorator

    @staticmethod
    def roles_required(*roles_required):
        """ all required roles have to be among the granted roles"""
        def decorator(f):
            @functools.wraps(f)
            def wrapper(*args, **kwargs):
                roles_required_set = set([str(n) for n in roles_required])
                roles_granted_set = asyncio.run(get_roles_as_set(kwargs['user']))
                if not roles_granted_set.issuperset(roles_required_set):
                    req_str = ' ,'.join(roles_required_set)
                    gran_str = ' ,'.join(roles_granted_set)
                    raise HTTPException(
                        status_code=HTTP_403_FORBIDDEN,
                        detail=f"roles of ACTIVE users required: {req_str} roles granted: {gran_str}"
                    )
                return f(*args, **kwargs)
            return wrapper
        return decorator


@router.post('/login', operation_id='post_api_user_login', response_model=Token)
async def post_api_user_login(form_data: OAuth2PasswordRequestForm = Depends()):
    user = await authenticate_user(form_data.username, form_data.password)
    if user is None:
        raise HTTPException(
            status_code=HTTP_401_UNAUTHORIZED,
            detail='Username unknown or password incorrect'
        )
    else:
        access_token = create_access_token(
            data={'sub': user.username},
            expires_delta=ACCESS_TOKEN_EXPIRES_TDT
        )
        return {'access_token': access_token, 'token_type': 'bearer'}
