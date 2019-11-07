from fastapi import APIRouter
from fastapi import Depends
from src.users.auth import get_current_user
from src.users.auth import get_current_active_user
from src.users.auth import get_current_super_user
from src.users.user_models import UserPy

router = APIRouter()


@router.get('/for-everyone')
def for_everyone():
    return f'Hello World!'


@router.get('/only-for-users')
def only_for_users(user: UserPy = Depends(get_current_user)):
    return f'Hello {user.username}!'


@router.get('/only-for-active-users')
def only_for_active_users(user: UserPy = Depends(get_current_active_user)):
    return f'Hello {user.username}! You active status is {user.is_active}!'


@router.get('/only-for-superusers')
def only_for_superusers(user: UserPy = Depends(get_current_super_user)):
    return f'Hello {user.username}! You are a superuser.'
