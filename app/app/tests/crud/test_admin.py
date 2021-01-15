from sqlalchemy.orm import Session

from app import crud
from app.schemas.users.admin import AdminUpdate
from app.schemas.users.user import UserCreate
from app.tests.utils.user import create_random_user
from app.tests.utils.utils import random_email, random_lower_string


def test_create_admin(db: Session) -> None:
    email = random_email()
    password = random_lower_string()
    user_in = UserCreate(email=email, password=password, type="admin")
    user = crud.user.create(db, obj_in=user_in)
    admin = crud.admin.get(db, user.id)
    assert hasattr(admin, "user_id")
    assert hasattr(admin, "permissions")


def test_check_if_user_is_admin(db: Session) -> None:
    user = create_random_user(db, "admin")
    admin = crud.admin.get(db, user.id)
    assert user.type == "admin"
    assert admin
    assert admin.permissions == 0


def test_update_user_admin(db: Session) -> None:
    user = create_random_user(db, "admin")
    admin = crud.admin.get(db, user.id)
    assert admin
    admin_update = AdminUpdate(user_id=user.id, permissions=5)
    crud.admin.update(db, db_obj=admin, obj_in=admin_update)
    user_2 = crud.admin.get(db, id=user.id)
    assert user_2
    assert user_2.permissions == 5
