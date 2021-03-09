from fastapi.encoders import jsonable_encoder
from sqlalchemy.orm import Session

from app import crud
from app.core.security import verify_password
from app.schemas import UserCreate, UserUpdate
from app.tests.utils.user import create_random_user
from app.tests.utils.utils import random_email, random_lower_string, random_password


def test_create_user_student(db: Session) -> None:
    email = random_email()
    password = random_password()
    user_in = UserCreate(email=email, password=password, type="student")
    user = crud.user.create(db, obj_in=user_in)
    assert user.email == email
    assert hasattr(user, "hashed_password")


def test_authenticate_user_student(db: Session) -> None:
    email = random_email()
    password = random_password()
    user_in = UserCreate(email=email, password=password, type="student")
    user = crud.user.create(db, obj_in=user_in)
    authenticated_user = crud.user.authenticate(db, email=email, password=password)
    assert authenticated_user
    assert user.email == authenticated_user.email


def test_authenticate_user_student_wrong_password(db: Session) -> None:
    email = random_email()
    password = random_password()
    user_in = UserCreate(email=email, password=password, type="student")
    crud.user.create(db, obj_in=user_in)
    authenticated_user = crud.user.authenticate(db, email=email, password=f"WRoNg{password}")
    assert authenticated_user is None


def test_not_authenticate_user(db: Session) -> None:
    email = random_email()
    password = random_password()
    user = crud.user.authenticate(db, email=email, password=password)
    assert user is None


def test_check_if_user_is_active_student(db: Session) -> None:
    user = create_random_user(db, type="student")
    is_active = crud.user.is_active(user)
    assert is_active is True


def test_check_if_user_is_superuser(db: Session) -> None:
    user = create_random_user(db, type="superuser")
    is_superuser = crud.user.is_superuser(user)
    assert is_superuser is True


def test_check_if_user_is_student(db: Session) -> None:
    user = create_random_user(db, type="student")
    assert user.type == "student"


def test_get_user_student(db: Session) -> None:
    user = create_random_user(db, type="student")
    user_2 = crud.user.get(db, id=user.id)
    assert user_2
    assert user.email == user_2.email
    assert jsonable_encoder(user) == jsonable_encoder(user_2)


def test_get_superuser(db: Session) -> None:
    user = create_random_user(db, type="superuser")
    user_2 = crud.user.get(db, id=user.id)
    assert user_2
    assert user.email == user_2.email
    assert jsonable_encoder(user) == jsonable_encoder(user_2)


def test_update_user_student(db: Session) -> None:
    user = create_random_user(db, type="student")
    new_password = random_password()
    user_in_update = UserUpdate(password=new_password)
    crud.user.update(db, db_obj=user, obj_in=user_in_update)
    user_2 = crud.user.get(db, id=user.id)
    assert user_2
    assert user.email == user_2.email
    assert verify_password(new_password, user_2.hashed_password)


def test_update_user_superuser(db: Session) -> None:
    user = create_random_user(db, type="superuser")
    db.refresh(user)
    new_password = random_password()
    user_in_update = UserUpdate(password=new_password, type="superuser")
    crud.user.update(db, db_obj=user, obj_in=user_in_update)
    user_2 = crud.user.get(db, id=user.id)
    assert user_2
    assert user.email == user_2.email
    assert verify_password(new_password, user_2.hashed_password)


def test_update_user_student_not_password(db: Session) -> None:
    user = create_random_user(db, type="student")
    full_name = random_lower_string()
    user_in_update = UserUpdate(full_name=full_name)
    crud.user.update(db, db_obj=user, obj_in=user_in_update)
    user_2 = crud.user.get(db, id=user.id)
    assert user_2
    assert user.email == user_2.email
    assert user.full_name == user_2.full_name


def test_update_superuser_not_password(db: Session) -> None:
    user = create_random_user(db, type="superuser")
    full_name = random_lower_string()
    user_in_update = UserUpdate(full_name=full_name, type="superuser")
    crud.user.update(db, db_obj=user, obj_in=user_in_update)
    user_2 = crud.user.get(db, id=user.id)
    assert user_2
    assert user.email == user_2.email
    assert user.full_name == user_2.full_name
