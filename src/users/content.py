from fastapi import APIRouter
from fastapi import Depends
from src.users.auth import get_current_user
from src.users.auth import get_current_active_user
from src.users.auth import get_current_super_user
from src.users.user_models import UserPy

router = APIRouter()


@router.get(
    '/for-everyone',
    operation_id='get_for_everyone',
    include_in_schema=False
)
def get_for_everyone():
    return f'Hello World!'


@router.get(
    '/only-for-users',
    operation_id='get_only_for_users',
    include_in_schema=False
)
def get_only_for_users(user: UserPy = Depends(get_current_user)):
    return f'Hello {user.username}!'


@router.get(
    '/only-for-active-users',
    operation_id='get_only_for_active_users',
    include_in_schema=False
)
def get_only_for_active_users(user: UserPy = Depends(get_current_active_user)):
    return f'Hello {user.username}! You active status is {user.is_active}!'


@router.get(
    '/only-for-superusers',
    operation_id='get_only_for_superusers',
    include_in_schema=False
)
def get_only_for_superusers(user: UserPy = Depends(get_current_super_user)):
    return f'Hello {user.username}! You are a superuser.'
