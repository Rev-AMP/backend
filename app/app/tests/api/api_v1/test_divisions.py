from random import randint
from typing import Dict

from sqlalchemy.orm import Session
from starlette.testclient import TestClient

from app import crud
from app.core.config import settings
from app.schemas.users.admin import AdminPermissions
from app.tests.utils.division import (
    create_random_course,
    create_random_division,
    create_random_professor,
)
from app.tests.utils.user import authentication_token_from_email, create_random_user
from app.tests.utils.utils import to_json


def test_get_all_divisions(client: TestClient, superuser_token_headers: Dict[str, str], db: Session) -> None:
    division = create_random_division(db)
    r = client.get(f"{settings.API_V1_STR}/divisions/", headers=superuser_token_headers)
    assert r.status_code == 200
    results = r.json()
    assert results
    assert results[-1] == to_json(division)


def test_get_division_existing(client: TestClient, superuser_token_headers: Dict[str, str], db: Session) -> None:
    division = create_random_division(db)
    r = client.get(f"{settings.API_V1_STR}/divisions/{division.id}", headers=superuser_token_headers)
    assert r.status_code == 200
    fetched_division = r.json()
    assert fetched_division
    assert fetched_division == to_json(division)


def test_get_division_nonexisting(client: TestClient, superuser_token_headers: Dict[str, str], db: Session) -> None:
    last_division_id = crud.division.get_multi(db)[-1].id
    r = client.get(f"{settings.API_V1_STR}/divisions/{last_division_id+1}", headers=superuser_token_headers)
    assert r.status_code == 404


def test_create_division(client: TestClient, superuser_token_headers: Dict[str, str], db: Session) -> None:
    course_id = create_random_course(db).id
    division_code = randint(1, 20)
    professor_id = create_random_professor(db).user_id
    data = {
        "course_id": course_id,
        "division_code": division_code,
        "professor_id": professor_id,
    }
    r = client.post(f"{settings.API_V1_STR}/divisions/", headers=superuser_token_headers, json=data)
    assert r.status_code == 200
    created_division = r.json()
    fetched_division = crud.division.get_by_details(
        db,
        course_id=course_id,
        division_code=division_code,
    )
    assert fetched_division
    assert created_division == to_json(fetched_division)
    assert data == {key: value for key, value in created_division.items() if key in data.keys()}


def test_create_division_existing(client: TestClient, superuser_token_headers: Dict[str, str], db: Session) -> None:
    division = create_random_division(db)
    data = {
        "course_id": division.course_id,
        "division_code": division.division_code,
        "professor_id": division.professor_id,
    }
    r = client.post(f"{settings.API_V1_STR}/divisions/", headers=superuser_token_headers, json=data)
    assert r.status_code == 409


def test_update_division(client: TestClient, superuser_token_headers: Dict[str, str], db: Session) -> None:
    division = create_random_division(db)
    assert division.professor_id
    professor_id = create_random_professor(db).user_id
    data = {"professor_id": professor_id}
    r = client.put(f"{settings.API_V1_STR}/divisions/{division.id}", headers=superuser_token_headers, json=data)
    fetched_division = r.json()
    assert fetched_division
    assert fetched_division["id"] == division.id
    assert fetched_division["professor_id"] == professor_id


def test_update_division_nonexisting(client: TestClient, superuser_token_headers: Dict[str, str], db: Session) -> None:
    last_division_id = crud.division.get_multi(db)[-1].id
    r = client.put(f"{settings.API_V1_STR}/divisions/{last_division_id + 1}", headers=superuser_token_headers, json={})
    assert r.status_code == 404


def test_delete_division(client: TestClient, superuser_token_headers: Dict[str, str], db: Session) -> None:
    division = create_random_division(db)
    r = client.delete(f"{settings.API_V1_STR}/divisions/{division.id}", headers=superuser_token_headers)
    assert r.status_code == 200
    deleted_division = crud.division.get(db, id=division.id)
    assert deleted_division is None


def test_delete_division_nonexisting(client: TestClient, superuser_token_headers: Dict[str, str], db: Session) -> None:
    last_division_id = crud.division.get_multi(db)[-1].id
    r = client.delete(f"{settings.API_V1_STR}/divisions/{last_division_id+1}", headers=superuser_token_headers)
    assert r.status_code == 404


def test_get_division_normal_user(client: TestClient, normal_user_token_headers: Dict[str, str], db: Session) -> None:
    r = client.get(f"{settings.API_V1_STR}/divisions/", headers=normal_user_token_headers)
    assert r.status_code == 403


def test_get_division_admin(client: TestClient, db: Session) -> None:
    admin_perms = AdminPermissions(0)
    admin_perms["course"] = True
    admin = create_random_user(db=db, type="admin", permissions=admin_perms.permissions)
    admin_user_token_headers = authentication_token_from_email(
        client=client, db=db, email=admin.email, user_type="admin"
    )
    r = client.get(f"{settings.API_V1_STR}/divisions/", headers=admin_user_token_headers)
    assert r.status_code == 200


def test_get_division_weakadmin(client: TestClient, db: Session) -> None:
    admin = create_random_user(db=db, type="admin", permissions=0)
    admin_user_token_headers = authentication_token_from_email(
        client=client, db=db, email=admin.email, user_type="admin"
    )
    r = client.get(f"{settings.API_V1_STR}/divisions/", headers=admin_user_token_headers)
    assert r.status_code == 403
