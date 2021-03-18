from typing import Dict

from sqlalchemy.orm import Session
from starlette.testclient import TestClient

from app import crud
from app.core.config import settings
from app.schemas.users.admin import AdminPermissions
from app.tests.utils.course import create_random_course, create_random_term
from app.tests.utils.user import authentication_token_from_email, create_random_user
from app.tests.utils.utils import random_lower_string, to_json


def test_get_all_courses(client: TestClient, superuser_token_headers: Dict[str, str], db: Session) -> None:
    course = create_random_course(db)
    r = client.get(f"{settings.API_V1_STR}/courses/", headers=superuser_token_headers)
    assert r.status_code == 200
    results = r.json()
    assert results
    assert results[-1]['name'] == course.name
    assert results[-1]['code'] == course.code
    assert results[-1]['term_id'] == course.term_id
    term = to_json(course.term)
    assert results[-1]['term'] == term


def test_get_course_existing(client: TestClient, superuser_token_headers: Dict[str, str], db: Session) -> None:
    course = create_random_course(db)
    r = client.get(f"{settings.API_V1_STR}/courses/{course.id}", headers=superuser_token_headers)
    assert r.status_code == 200
    fetched_course = r.json()
    assert fetched_course
    assert fetched_course['id'] == course.id
    assert fetched_course['name'] == course.name
    assert fetched_course['code'] == course.code
    assert fetched_course['term_id'] == course.term_id


def test_get_course_nonexisting(client: TestClient, superuser_token_headers: Dict[str, str], db: Session) -> None:
    last_course_id = crud.course.get_multi(db)[-1].id
    r = client.get(f"{settings.API_V1_STR}/courses/{last_course_id+1}", headers=superuser_token_headers)
    assert r.status_code == 404


def test_create_course(client: TestClient, superuser_token_headers: Dict[str, str], db: Session) -> None:
    name = random_lower_string()
    code = random_lower_string()[:20]
    term_id = create_random_term(db).id
    data = {
        'name': name,
        'code': code,
        'term_id': term_id,
    }
    r = client.post(f"{settings.API_V1_STR}/courses/", headers=superuser_token_headers, json=data)
    assert r.status_code == 200
    created_course = r.json()
    fetched_course = crud.course.get_by_details(
        db,
        name=name,
        code=code,
        term_id=term_id,
    )
    assert fetched_course
    assert created_course['name'] == fetched_course.name == name
    assert created_course['code'] == fetched_course.code == code
    assert created_course['term_id'] == fetched_course.term_id == term_id


def test_create_course_existing(client: TestClient, superuser_token_headers: Dict[str, str], db: Session) -> None:
    course = create_random_course(db)
    data = {
        'name': course.name,
        'code': course.code,
        'term_id': course.term_id,
    }
    r = client.post(f"{settings.API_V1_STR}/courses/", headers=superuser_token_headers, json=data)
    assert r.status_code == 409


def test_update_course(client: TestClient, superuser_token_headers: Dict[str, str], db: Session) -> None:
    course = create_random_course(db)
    assert course.name
    name = random_lower_string()
    data = {'name': name}
    r = client.put(f"{settings.API_V1_STR}/courses/{course.id}", headers=superuser_token_headers, json=data)
    fetched_course = r.json()
    assert fetched_course
    assert fetched_course['id'] == course.id
    assert fetched_course['name'] == name


def test_update_course_nonexisting(client: TestClient, superuser_token_headers: Dict[str, str], db: Session) -> None:
    last_course_id = crud.course.get_multi(db)[-1].id
    r = client.put(f"{settings.API_V1_STR}/courses/{last_course_id + 1}", headers=superuser_token_headers, json={})
    assert r.status_code == 404


def test_delete_course(client: TestClient, superuser_token_headers: Dict[str, str], db: Session) -> None:
    course = create_random_course(db)
    r = client.delete(f"{settings.API_V1_STR}/courses/{course.id}", headers=superuser_token_headers)
    assert r.status_code == 200
    deleted_course = crud.course.get(db, id=course.id)
    assert deleted_course is None


def test_delete_course_nonexisting(client: TestClient, superuser_token_headers: Dict[str, str], db: Session) -> None:
    last_course_id = crud.course.get_multi(db)[-1].id
    r = client.delete(f"{settings.API_V1_STR}/courses/{last_course_id+1}", headers=superuser_token_headers)
    assert r.status_code == 404


def test_get_course_normal_user(client: TestClient, normal_user_token_headers: Dict[str, str], db: Session) -> None:
    r = client.get(f"{settings.API_V1_STR}/courses/", headers=normal_user_token_headers)
    assert r.status_code == 403


def test_get_course_admin(client: TestClient, db: Session) -> None:
    admin_perms = AdminPermissions(0)
    admin_perms['course'] = True
    admin = create_random_user(db=db, type="admin", permissions=admin_perms.permissions)
    admin_user_token_headers = authentication_token_from_email(
        client=client, db=db, email=admin.email, user_type='admin'
    )
    r = client.get(f"{settings.API_V1_STR}/courses/", headers=admin_user_token_headers)
    assert r.status_code == 200


def test_get_course_weakadmin(client: TestClient, db: Session) -> None:
    admin = create_random_user(db=db, type="admin", permissions=0)
    admin_user_token_headers = authentication_token_from_email(
        client=client, db=db, email=admin.email, user_type='admin'
    )
    r = client.get(f"{settings.API_V1_STR}/courses/", headers=admin_user_token_headers)
    assert r.status_code == 403
