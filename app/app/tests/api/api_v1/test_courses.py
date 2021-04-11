from typing import Dict

from sqlalchemy.orm import Session
from starlette.testclient import TestClient

from app import crud
from app.core.config import settings
from app.schemas.users.admin import AdminPermissions
from app.tests.utils.course import create_random_course, create_random_term
from app.tests.utils.user import authentication_token_from_email, create_random_user
from app.tests.utils.utils import (
    compare_api_and_db_query_results,
    random_lower_string,
    to_json,
)
from app.utils import generate_uuid


def test_get_all_courses(client: TestClient, superuser_token_headers: Dict[str, str], db: Session) -> None:
    course = create_random_course(db)
    r = client.get(f"{settings.API_V1_STR}/courses/", headers=superuser_token_headers)
    assert r.status_code == 200
    results = r.json()
    assert results
    compare_api_and_db_query_results(api_result=results[-1], db_dict=to_json(course))


def test_get_course_existing(client: TestClient, superuser_token_headers: Dict[str, str], db: Session) -> None:
    course = create_random_course(db)
    r = client.get(f"{settings.API_V1_STR}/courses/{course.id}", headers=superuser_token_headers)
    assert r.status_code == 200
    fetched_course = r.json()
    assert fetched_course
    compare_api_and_db_query_results(api_result=fetched_course, db_dict=to_json(course))


def test_get_course_nonexisting(client: TestClient, superuser_token_headers: Dict[str, str], db: Session) -> None:
    r = client.get(f"{settings.API_V1_STR}/courses/{generate_uuid()}", headers=superuser_token_headers)
    assert r.status_code == 404


def test_create_course(client: TestClient, superuser_token_headers: Dict[str, str], db: Session) -> None:
    name = random_lower_string()
    course_code = random_lower_string()[:20]
    elective_code = random_lower_string()[:20]
    term_id = create_random_term(db).id
    data = {
        "name": name,
        "course_code": course_code,
        "elective_code": elective_code,
        "term_id": term_id,
    }
    r = client.post(f"{settings.API_V1_STR}/courses/", headers=superuser_token_headers, json=data)
    assert r.status_code == 200
    created_course = r.json()
    fetched_course = crud.course.get_by_details(
        db,
        name=name,
        course_code=course_code,
        term_id=term_id,
    )
    assert fetched_course
    compare_api_and_db_query_results(api_result=created_course, db_dict=to_json(fetched_course))
    compare_api_and_db_query_results(data, created_course)


def test_create_course_existing(client: TestClient, superuser_token_headers: Dict[str, str], db: Session) -> None:
    course = create_random_course(db)
    data = {
        "name": course.name,
        "course_code": course.course_code,
        "term_id": course.term_id,
    }
    r = client.post(f"{settings.API_V1_STR}/courses/", headers=superuser_token_headers, json=data)
    assert r.status_code == 409


def test_update_course(client: TestClient, superuser_token_headers: Dict[str, str], db: Session) -> None:
    course = create_random_course(db)
    assert course.name
    name = random_lower_string()
    data = {"name": name}
    r = client.put(f"{settings.API_V1_STR}/courses/{course.id}", headers=superuser_token_headers, json=data)
    fetched_course = r.json()
    db.refresh(course)
    assert fetched_course
    compare_api_and_db_query_results(api_result=fetched_course, db_dict=to_json(course))


def test_update_course_nonexisting(client: TestClient, superuser_token_headers: Dict[str, str], db: Session) -> None:
    r = client.put(f"{settings.API_V1_STR}/courses/{generate_uuid()}", headers=superuser_token_headers, json={})
    assert r.status_code == 404


def test_delete_course(client: TestClient, superuser_token_headers: Dict[str, str], db: Session) -> None:
    course = create_random_course(db)
    r = client.delete(f"{settings.API_V1_STR}/courses/{course.id}", headers=superuser_token_headers)
    assert r.status_code == 200
    deleted_course = crud.course.get(db, id=course.id)
    assert deleted_course is None


def test_delete_course_nonexisting(client: TestClient, superuser_token_headers: Dict[str, str], db: Session) -> None:
    r = client.delete(f"{settings.API_V1_STR}/courses/{generate_uuid()}", headers=superuser_token_headers)
    assert r.status_code == 404


def test_get_course_normal_user(client: TestClient, normal_user_token_headers: Dict[str, str], db: Session) -> None:
    r = client.get(f"{settings.API_V1_STR}/courses/", headers=normal_user_token_headers)
    assert r.status_code == 403


def test_get_course_admin(client: TestClient, db: Session) -> None:
    admin_perms = AdminPermissions(0)
    admin_perms["course"] = True
    admin = create_random_user(db=db, type="admin", permissions=admin_perms.permissions)
    admin_user_token_headers = authentication_token_from_email(
        client=client, db=db, email=admin.email, user_type="admin"
    )
    r = client.get(f"{settings.API_V1_STR}/courses/", headers=admin_user_token_headers)
    assert r.status_code == 200


def test_get_course_weakadmin(client: TestClient, db: Session) -> None:
    admin = create_random_user(db=db, type="admin", permissions=0)
    admin_user_token_headers = authentication_token_from_email(
        client=client, db=db, email=admin.email, user_type="admin"
    )
    r = client.get(f"{settings.API_V1_STR}/courses/", headers=admin_user_token_headers)
    assert r.status_code == 403
