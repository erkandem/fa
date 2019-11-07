from fastapi import APIRouter
from fastapi import Depends

from src.users.auth import bouncer
from src.users.auth import get_current_active_user
from src.users.user_models import UserPy

router = APIRouter()


@router.get('/for-everyone')
def for_everyone():
    return f'Hello World!'


@router.get('/only-for-active-users')
@bouncer.roles_required('user')
def only_for_active_users(user: UserPy = Depends(get_current_active_user)):
    return f'Hello {user.username}! You active status is {user.is_active}!'


@router.get('/only-for-superusers')
@bouncer.roles_required('superuser')
def only_for_superusers(user: UserPy = Depends(get_current_active_user)):
    return f'Hello {user.username}! You are a superuser.'


@router.get('/only-for-active-superusers-and-active-users')
@bouncer.roles_accepted('superuser', 'user')
def only_for_active_superusers_and_active_users(user: UserPy = Depends(get_current_active_user)):
    return f'Hello, {user.username}'
