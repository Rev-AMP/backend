from typing import Dict, Optional

from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app import crud
from app.core.config import settings
from app.models import User
from app.schemas import AdminUpdate, UserCreate, UserUpdate
from app.tests.utils.utils import random_email, random_lower_string


def user_authentication_headers(*, client: TestClient, email: str, password: str) -> Dict[str, str]:
    data = {"username": email, "password": password}

    r = client.post(f"{settings.API_V1_STR}/login/access-token", data=data)
    response = r.json()
    auth_token = response["access_token"]
    headers = {"Authorization": f"Bearer {auth_token}"}
    return headers


def create_random_user(
    db: Session, type: str, is_admin: bool = False, school: Optional[int] = None, permissions: Optional[int] = None
) -> User:
    """
    :param db: SQLAlchemy Session object pointing to the project database
    :param type: Type of user to create
    :param is_admin: True if user is an auxilary admin, else False
    :param school: School that the user belongs to (optional)
    :param permissions: permissions to be set if user is an admin
    :return: User object created from random values and given type
    """
    email = random_email()
    password = random_lower_string()
    user_in = UserCreate(email=email, password=password, type=type, is_admin=is_admin, school=school)
    user = crud.user.create(db=db, obj_in=user_in)
    if user.is_admin and permissions:
        if admin := crud.admin.get(db, user.id):
            admin_in = AdminUpdate(user_id=user.id, permissions=permissions)
            crud.admin.update(db=db, db_obj=admin, obj_in=admin_in)
    return user


def authentication_token_from_email(
    *, client: TestClient, email: str, db: Session, user_type: str = "student", school: Optional[int] = None
) -> Dict[str, str]:
    """
    Return a valid token for the user with given email.

    If the user doesn't exist it is created first.
    """
    password = random_lower_string()
    user = crud.user.get_by_email(db, email=email)
    if not user:
        user_in_create = UserCreate(email=email, password=password, type=user_type, school=school)
        user = crud.user.create(db, obj_in=user_in_create)
    else:
        user_in_update = UserUpdate(password=password)
        user = crud.user.update(db, db_obj=user, obj_in=user_in_update)

    return user_authentication_headers(client=client, email=email, password=password)
