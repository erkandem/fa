from fastapi import APIRouter
from fastapi import Depends

from src.users.auth import bouncer
from src.users.auth import get_current_active_user
from src.users.user_models import UserPy

router = APIRouter()


@router.get(
    '/for-everyone',
    operation_id='get_for_everyone_decorated',
    include_in_schema=False
)
def get_for_everyone_decorated():
    return f'Hello World!'


@router.get(
    '/only-for-active-users',
    operation_id='get_only_for_active_users_decorated',
    include_in_schema=False
)
@bouncer.roles_required('user')
def get_only_for_active_users_decorated(user: UserPy = Depends(get_current_active_user)):
    return f'Hello {user.username}! You active status is {user.is_active}!'


@router.get(
    '/only-for-superusers',
    operation_id='get_only_for_superusers_decorated',
    include_in_schema=False
)
@bouncer.roles_required('superuser')
def get_only_for_superusers_decorated(user: UserPy = Depends(get_current_active_user)):
    return f'Hello {user.username}! You are a superuser.'


@router.get(
    '/only-for-active-superusers-and-active-users',
    operation_id='get_only_for_active_superusers_and_active_users_decorated',
    include_in_schema=False
)
@bouncer.roles_accepted('superuser', 'user')
def get_only_for_active_superusers_and_active_users_decorated(user: UserPy = Depends(get_current_active_user)):
    return f'Hello, {user.username}'
