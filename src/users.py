import json
import os
import uuid
from datetime import(
    datetime,
    timedelta,
)
import logging
import typing as t

from fastapi import (
    Depends,
    APIRouter,
    HTTPException,
    status,
)
from fastapi.security import (
    OAuth2PasswordBearer,
    OAuth2PasswordRequestForm,
)
from jose import(
    JWTError,
    jwt,
)
from passlib.context import CryptContext
import pydantic
from pydantic import (
    BaseModel,
    EmailStr,
)
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm.session import Session

import appconfig
from src.db import (
    get_users_db,
    results_proxy_to_list_of_dict, get_async_users_db,
)
from databases.core import Connection


logger = logging.getLogger(__name__)


SUPERUSER_ROLE_STR = "superuser"
USER_ROLE_STR = "user"
ROLE_STRINGS_SET = {
    SUPERUSER_ROLE_STR,
    USER_ROLE_STR,
}

from timeit import timeit
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
#                       Los User modeles                                      #
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
class User(BaseModel):
    uid: t.Optional[uuid.UUID] = None
    username: str
    email: t.Optional[EmailStr] = None
    full_name: t.Optional[str] = None
    is_active: t.Optional[bool] = True
    roles: t.Optional[str] = USER_ROLE_STR

    @pydantic.validator("uid", pre=True, always=True)
    def default_id(cls, v):
        return v or str(uuid.uuid4())

    @pydantic.validator("roles")
    def validate_roles(cls, v):
        if get_roles_as_set(v).issubset(ROLE_STRINGS_SET):
            return v


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    username: t.Optional[str] = None


class UserInDB(User):
    hashed_salted_pwd: str


class UserCreation(User):
    password: str


# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
#                       El Database                                           #
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
metadata = sa.MetaData()
users_table = sa.Table(
    "users",
    metadata,
    sa.Column("uid", UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True, unique=True),
    sa.Column("username", sa.String, unique=True, index=True),
    sa.Column("full_name", sa.String),
    sa.Column("email", sa.String, unique=True),
    sa.Column("hashed_salted_pwd", sa.String),
    sa.Column("is_active", sa.Boolean, default=True),
    sa.Column("roles", sa.String, default=USER_ROLE_STR)
)


def table_creation(url: str = None):
    """
    Only relevant for sqlalchemy managed tables
    """
    logger.debug("creating tables")
    if url is None:
        url = appconfig.DATABASE_URL_APPLICATION_DB
    engine = sa.create_engine(url)
    metadata.create_all(engine)
    engine.dispose()
    logger.debug("created tables")


class UserCrud:
    @staticmethod
    def insert_new_user(
            user: UserInDB,
            con: Session
    ) -> t.Tuple[UserInDB, bool]:
        try:
            con.execute(users_table.insert(),  user.dict())
            is_new = True
        except IntegrityError:
            is_new = False
        user_in_db = UserCrud.select_user_by_username(user.username, con)
        return user_in_db, is_new

    @staticmethod
    def select_user_by_username(
            username: str,
            con: Session
    ) -> t.Optional[UserInDB]:
        user_cursor = con.execute(users_table.select().where(users_table.c.username == username))
        try:
            user_in_db_dict = results_proxy_to_list_of_dict(user_cursor)[0]
        except IndexError:
            return None
        user_in_db = UserInDB(**user_in_db_dict)
        return user_in_db

    @staticmethod
    async def async_select_user_by_username(
            username: str,
            con: Connection,
    ) -> t.Optional[UserInDB]:
        result = await con.fetch_all(
            'SELECT * from users where username = :username;',
            values={
                'username': username,
            }
        )
        try:
            user_in_db_dict = results_proxy_to_list_of_dict(result)[0]
        except IndexError:
            return None
        user_in_db = UserInDB(**user_in_db_dict)
        return user_in_db

    @staticmethod
    def delete_user_by_username(
            username: str,
            con: Session
    ) -> bool:
        user = UserCrud.select_user_by_username(username, con)
        if user is None:
            return False
        con.execute(users_table.delete().where(users_table.c.username == username))
        return True

import asyncpg
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
#                       Los Utilities                                         #
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
def load_superuser() -> t.Dict[str, t.Any]:
    data_str = os.getenv("DEFAULT_API_SUPER_USER")
    data = json.loads(data_str)
    return data


def load_other_default_users() -> t.List[t.Dict[str, t.Any]]:
    data_str = os.getenv("DEFAULT_API_USERS")
    data = json.loads(data_str)
    return data


def load_all_default_users() -> t.List[t.Dict[str, t.Any]]:
    su = load_superuser()
    du = load_other_default_users()
    return [su] + du


def create_default_users():
    logger.debug('creating all default users')
    url = appconfig.DATABASE_URL_APPLICATION_DB
    engine = sa.create_engine(url)
    local_sessionmaker = sessionmaker(bind=engine, autocommit=True)
    session = local_sessionmaker()
    user_data = load_all_default_users()
    for user_dict in user_data:
        user = UserCreation(**user_dict)
        _inserted_user, _is_new = hash_and_insert_new_user(user, session)

    session.close()
    engine.dispose()
    logger.debug('created all default users')


def hash_and_insert_new_user(
        input_user: UserCreation,
        con: Session
) -> t.Tuple[UserInDB, bool]:
    input_user_dict = input_user.dict()
    input_user_dict["hashed_salted_pwd"] = get_password_hash(input_user_dict["password"])
    user = UserInDB(**input_user_dict)
    user_in_db, is_new = UserCrud.insert_new_user(user, con)
    return user_in_db, is_new


def get_roles_as_set(roles: str) -> t.Set[str]:
    return set(roles.split(","))


def get_roles_as_str(roles: t.Set[str]) -> str:
    return ",".join(roles)


# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
#                       El App and security thing                             #
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
users_router = APIRouter()
auth_router = APIRouter()
testing_router = APIRouter()
pwd_context = CryptContext(
    schemes=[appconfig.PASSWORD_HASHING_ALGORITHM],
    deprecated="auto",
)
oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl="token",
)


# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
#                       Los Utilities                                         #
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
def verify_password(
        plain_password: str,
        hashed_password: str,
) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    """ salting is done by default"""
    return pwd_context.hash(password)


async def authenticate_user(
        username: str,
        password: str,
        con: Connection,
) -> t.Union[User, bool]:
    user = await UserCrud.async_select_user_by_username(username, con)
    if not user:
        return False
    if not verify_password(password, user.hashed_salted_pwd):
        return False
    return user


def create_access_token(
        data: t.Dict[str, t.Any],
        expires_delta: t.Optional[timedelta] = None
) -> str:
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + appconfig.ACCESS_TOKEN_EXPIRES_TIMEDELTA
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(
        to_encode,
        appconfig.IVOLAPI_SECRET_KEY,
        algorithm=appconfig.TOKEN_SIGNING_ALGORITHM
    )
    return encoded_jwt


async def get_current_user(
        token: str = Depends(oauth2_scheme),
        con: Connection = Depends(get_async_users_db),
) -> User:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(
            token,
            appconfig.IVOLAPI_SECRET_KEY,
            algorithms=[
                appconfig.TOKEN_SIGNING_ALGORITHM,
            ]
        )
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
        token_data = TokenData(username=username)
    except JWTError:
        raise credentials_exception
    user_in_db = await UserCrud.async_select_user_by_username(
        token_data.username,
        con,
    )
    if user_in_db is None:
        raise credentials_exception
    user = User(**user_in_db.dict())  # don't expose the password
    return user


async def get_current_active_user(current_user: User = Depends(get_current_user)):
    if not current_user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Inactive user",
        )
    return current_user


async def get_current_active_superuser(current_user: User = Depends(get_current_active_user)):
    superuser_role_checker(current_user)
    return current_user


async def get_current_authenticated_user(current_user: User = Depends(get_current_active_user)):
    """ role based equivalent to get_current_active_user"""
    any_role_checker(current_user)
    return current_user


# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
#                       El RoleChecker                                        #
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
class RoleChecker:
    """
    based on https://learnings.desipenguin.com/post/rolechecker-with-fastapi/
    """
    def __init__(self, allowed_roles: t.Set[str]):
        self.allowed_roles = allowed_roles

    def __call__(self, user: User):
        if not get_roles_as_set(user.roles) not in self.allowed_roles:
            logger.debug(f"User with role {user.roles} not in {self.allowed_roles}")
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Required role missing",
            )


superuser_role_checker = RoleChecker({SUPERUSER_ROLE_STR, })
user_role_checker = RoleChecker({USER_ROLE_STR, })
any_role_checker = RoleChecker(ROLE_STRINGS_SET)


# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
#                           Los Views                                         #
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
@auth_router.post(
    "/token",
    response_model=Token,
    operation_id="post_login_for_access_token",
)
async def post_login_for_access_token(
        form_data: OAuth2PasswordRequestForm = Depends(),
        con: Connection = Depends(get_async_users_db),
):
    """endpoint to return API access token with your valid login data"""
    user = await authenticate_user(
        form_data.username,
        form_data.password,
        con,
    )
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token = create_access_token(
        data={"sub": user.username},
        expires_delta=appconfig.ACCESS_TOKEN_EXPIRES_TIMEDELTA,
    )
    return {"access_token": access_token, "token_type": "bearer"}


@users_router.get(
    "/users/",
    response_model=User,
    operation_id="get_user_by_username",
)
async def get_user_by_username(
        username: str,
        current_user: User = Depends(get_current_active_superuser),
        con: Session = Depends(get_users_db),
):
    """
    get a user object from the username
    """
    user = UserCrud.select_user_by_username(username, con)
    if user is None:
        raise HTTPException(
            status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )
    return user


@users_router.post(
    "/users/",
    response_model=User,
    operation_id="post_create_user",
)
async def post_create_user(
        input_user: UserCreation,
        current_user: User = Depends(get_current_active_superuser),
        con: Session = Depends(get_users_db),
):
    """
    Create a new user for the API
    the UUID field is optional. Don't include it, or send ``null`` to be safe
    """
    inserted_user, _is_new = hash_and_insert_new_user(input_user, con)
    user = User(**inserted_user.dict())
    return user


@users_router.delete(
    "/users/",
    status_code=status.HTTP_204_NO_CONTENT,
    operation_id="delete_user_by_username",
)
async def delete_user_by_username(
        username: str,
        current_user: User = Depends(get_current_active_superuser),
        con: Session = Depends(get_users_db),
):
    """ Delete a user """
    existed = UserCrud.delete_user_by_username(username, con)
    if not existed:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )


@testing_router.get(
    "/any-authenticated-users/",
    operation_id="get_for_active_user_role",
    include_in_schema=False,
)
def get_for_active_user_role(user: User = Depends(get_current_authenticated_user)):
    """equivalent to  ``get_for_users``"""
    return {
        "user": user,
    }


@testing_router.get(
    "/any-active-user/",
    operation_id="get_for_users",
    include_in_schema=False,
)
def get_for_users(user: User = Depends(get_current_active_user)):
    return {
        "user": user,
    }


@testing_router.get(
    "/some-resource-for-superusers-only/",
    operation_id="get_for_superusers",
    include_in_schema=False,
)
def get_for_superusers(user: User = Depends(get_current_active_superuser)):
    return {
        "user": user,
    }
