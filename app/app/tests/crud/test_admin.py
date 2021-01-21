from sqlalchemy.orm import Session

from app import crud
from app.schemas import AdminUpdate
from app.tests.utils.user import create_random_user


def test_create_admin(db: Session) -> None:
    user = create_random_user(db=db, type="admin")
    admin = crud.admin.get(db, user.id)
    assert hasattr(admin, "user_id")
    assert hasattr(admin, "permissions")


def test_check_if_user_is_admin(db: Session) -> None:
    user = create_random_user(db=db, type="admin")
    admin = crud.admin.get(db, user.id)
    assert user.type == "admin"
    assert admin
    assert admin.permissions == 0


def test_update_user_admin(db: Session) -> None:
    user = create_random_user(db=db, type="admin")
    admin = crud.admin.get(db, user.id)
    assert admin
    admin_update = AdminUpdate(user_id=user.id, permissions=5)
    crud.admin.update(db, db_obj=admin, obj_in=admin_update)
    user_2 = crud.admin.get(db, id=user.id)
    assert user_2
    assert user_2.permissions == 5
