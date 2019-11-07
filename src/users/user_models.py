import os
from typing import Optional
import uuid
import pydantic
from pydantic import BaseModel
from pydantic.types import EmailStr


class UserPy(BaseModel):
    uid: Optional[str] = None
    username: Optional[str] = None
    email: Optional[EmailStr]
    salt: Optional[str] = None
    hashed_salted_pwd: Optional[str] = None
    is_active: Optional[bool] = True
    roles: Optional[str] = 'user'

    @pydantic.validator('uid', pre=True, always=True)
    def default_id(cls, v):
        return v or str(uuid.uuid4())

    @pydantic.validator('salt', pre=True, always=True)
    def default_salt(cls, v):
        return v or str(os.urandom(32).hex())


class RegisterPy(BaseModel):
    username: str
    password: str


class DeleteUserPy(BaseModel):
    username: str


class UpdatePassword(BaseModel):
    password: str
    new_password: str
