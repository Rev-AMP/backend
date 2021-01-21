from random import randint
from typing import Dict

from sqlalchemy.orm import Session
from starlette.testclient import TestClient

from app import crud
from app.core.config import settings
from app.tests.utils.school import create_random_school
from app.tests.utils.user import authentication_token_from_email, create_random_user
from app.tests.utils.utils import random_email, random_lower_string


def test_get_all_schools(client: TestClient, superuser_token_headers: Dict[str, str], db: Session) -> None:
    school = create_random_school(db)
    r = client.get(f"{settings.API_V1_STR}/schools/", headers=superuser_token_headers)
    assert 200 <= r.status_code < 300
    results = r.json()
    assert results
    assert results[0]['id'] == school.id
    assert results[0]['name'] == school.name
    assert results[0]['head'] == school.head


def test_create_school(client: TestClient, superuser_token_headers: Dict[str, str], db: Session) -> None:
    name = random_lower_string()
    head = random_lower_string()
    data = {'name': name, 'head': head}
    r = client.post(f"{settings.API_V1_STR}/schools/", headers=superuser_token_headers, json=data)
    assert 200 <= r.status_code < 300
    created_school = r.json()
    school = crud.school.get_by_name(db, name=name)
    assert school
    assert created_school['name'] == school.name == name
    assert created_school['head'] == school.head == head


def test_create_school_existing(client: TestClient, superuser_token_headers: Dict[str, str], db: Session) -> None:
    school = create_random_school(db)
    data = {'name': school.name, 'head': school.head}
    r = client.post(f"{settings.API_V1_STR}/schools/", headers=superuser_token_headers, json=data)
    assert 400 <= r.status_code < 500


def test_get_school_superuser(client: TestClient, superuser_token_headers: Dict[str, str], db: Session) -> None:
    school = create_random_school(db)
    r = client.get(f"{settings.API_V1_STR}/schools/{school.id}", headers=superuser_token_headers)
    assert 200 <= r.status_code < 300
    fetched_school = r.json()
    assert fetched_school
    assert fetched_school['id'] == school.id
    assert fetched_school['name'] == school.name
    assert fetched_school['head'] == school.head


def test_get_school_admin(client: TestClient, db: Session) -> None:
    school = create_random_school(db)
    admin_user_token_headers = authentication_token_from_email(
        client=client, db=db, email=random_email(), user_type="admin"
    )
    r = client.get(f"{settings.API_V1_STR}/schools/{school.id}", headers=admin_user_token_headers)
    assert 200 <= r.status_code < 300
    fetched_school = r.json()
    assert fetched_school
    assert fetched_school['id'] == school.id
    assert fetched_school['name'] == school.name
    assert fetched_school['head'] == school.head


def test_get_school_valid_student(client: TestClient, db: Session) -> None:
    school = create_random_school(db)
    admin_user_token_headers = authentication_token_from_email(
        client=client, db=db, email=random_email(), school=school.id
    )
    r = client.get(f"{settings.API_V1_STR}/schools/{school.id}", headers=admin_user_token_headers)
    assert 200 <= r.status_code < 300
    fetched_school = r.json()
    assert fetched_school
    assert fetched_school['id'] == school.id
    assert fetched_school['name'] == school.name
    assert fetched_school['head'] == school.head


def test_get_school_invalid_student(client: TestClient, db: Session) -> None:
    school = create_random_school(db)
    admin_user_token_headers = authentication_token_from_email(client=client, db=db, email=random_email())
    r = client.get(f"{settings.API_V1_STR}/schools/{school.id}", headers=admin_user_token_headers)
    assert 400 <= r.status_code < 500


def test_update_school(client: TestClient, superuser_token_headers: Dict[str, str], db: Session) -> None:
    school = create_random_school(db)
    new_name = random_lower_string()
    data = {'name': new_name, 'head': school.head}
    r = client.put(f"{settings.API_V1_STR}/schools/{school.id}", headers=superuser_token_headers, json=data)
    assert 200 <= r.status_code < 300
    fetched_school = r.json()
    db.refresh(school)
    assert fetched_school
    assert fetched_school['id'] == school.id
    assert fetched_school['name'] == school.name == new_name
    assert fetched_school['head'] == school.head


def test_update_school_nonexisting(client: TestClient, superuser_token_headers: Dict[str, str], db: Session) -> None:
    while crud.school.get(db, id=(school_id := randint(0, 10000000))):
        pass
    data = {'name': random_lower_string(), 'head': random_lower_string()}
    r = client.put(f"{settings.API_V1_STR}/schools/{school_id}", headers=superuser_token_headers, json=data)
    assert 400 <= r.status_code < 500


def test_get_all_students(client: TestClient, superuser_token_headers: Dict[str, str], db: Session) -> None:
    school = create_random_school(db)
    school_student = create_random_user(db=db, type="student", school=school.id)
    r = client.get(f"{settings.API_V1_STR}/schools/{school.id}/students", headers=superuser_token_headers)
    assert 200 <= r.status_code < 300
    fetched_students = r.json()
    assert fetched_students
    assert fetched_students[0]['id'] == school_student.id
    assert fetched_students[0]['full_name'] == school_student.full_name
    assert fetched_students[0]['email'] == school_student.email
    assert fetched_students[0]['type'] == school_student.type
    assert fetched_students[0]['is_admin'] == school_student.is_admin
    assert fetched_students[0]['profile_picture'] == school_student.profile_picture


def test_get_all_professors(client: TestClient, superuser_token_headers: Dict[str, str], db: Session) -> None:
    school = create_random_school(db)
    school_student = create_random_user(db=db, type="professor", school=school.id)
    r = client.get(f"{settings.API_V1_STR}/schools/{school.id}/professors", headers=superuser_token_headers)
    assert 200 <= r.status_code < 300
    fetched_students = r.json()
    assert fetched_students
    assert fetched_students[0]['id'] == school_student.id
    assert fetched_students[0]['full_name'] == school_student.full_name
    assert fetched_students[0]['email'] == school_student.email
    assert fetched_students[0]['type'] == school_student.type
    assert fetched_students[0]['is_admin'] == school_student.is_admin
    assert fetched_students[0]['profile_picture'] == school_student.profile_picture
