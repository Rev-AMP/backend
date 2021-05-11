from datetime import datetime, timedelta
from random import choice, randint
from typing import Dict

from sqlalchemy.orm import Session
from starlette.testclient import TestClient

from app import crud
from app.core.config import settings
from app.schemas import StudentUpdate
from app.schemas.users.admin import AdminPermissions
from app.tests.utils.school import create_random_school
from app.tests.utils.student import create_random_student
from app.tests.utils.term import create_random_term, create_random_year
from app.tests.utils.user import authentication_token_from_email, create_random_user
from app.tests.utils.utils import (
    compare_api_and_db_query_results,
    random_lower_string,
    to_json,
)
from app.utils import generate_uuid


def test_get_all_terms(client: TestClient, superuser_token_headers: Dict[str, str], db: Session) -> None:
    term = create_random_term(db=db)
    r = client.get(f"{settings.API_V1_STR}/terms/", headers=superuser_token_headers)
    assert r.status_code == 200
    results = r.json()
    assert results
    compare_api_and_db_query_results(api_result=results[-1], db_dict=to_json(term))


def test_get_terms_admin(client: TestClient, db: Session) -> None:
    admin_perms = AdminPermissions(0)
    admin_perms["term"] = True
    admin = create_random_user(db=db, type="admin", permissions=admin_perms.permissions)
    admin_user_token_headers = authentication_token_from_email(
        client=client, db=db, email=admin.email, user_type="admin"
    )
    r = client.get(f"{settings.API_V1_STR}/terms/", headers=admin_user_token_headers)
    assert r.status_code == 200


def test_get_terms_weakadmin(client: TestClient, db: Session) -> None:
    admin = create_random_user(db=db, type="admin", permissions=0)
    admin_user_token_headers = authentication_token_from_email(
        client=client, db=db, email=admin.email, user_type="admin"
    )
    r = client.get(f"{settings.API_V1_STR}/terms/", headers=admin_user_token_headers)
    assert r.status_code == 403


def test_get_term_existing(client: TestClient, superuser_token_headers: Dict[str, str], db: Session) -> None:
    term = create_random_term(db=db)
    r = client.get(f"{settings.API_V1_STR}/terms/{term.id}", headers=superuser_token_headers)
    assert r.status_code == 200
    fetched_term = r.json()
    assert fetched_term
    compare_api_and_db_query_results(api_result=fetched_term, db_dict=to_json(term))


def test_get_term_nonexisting(client: TestClient, superuser_token_headers: Dict[str, str], db: Session) -> None:
    r = client.get(f"{settings.API_V1_STR}/terms/{generate_uuid()}", headers=superuser_token_headers)
    assert r.status_code == 404


def test_get_term_students(client: TestClient, superuser_token_headers: Dict[str, str], db: Session) -> None:
    term = create_random_term(db=db)
    student = create_random_student(db=db, term_id=term.id)
    db.refresh(term)
    assert term.students[-1] == student
    r = client.get(f"{settings.API_V1_STR}/terms/{term.id}/students", headers=superuser_token_headers)
    assert r.status_code == 200
    students = r.json()
    assert students
    for api_obj, db_obj in zip(students, term.students):
        compare_api_and_db_query_results(api_result=api_obj, db_dict=to_json(db_obj))


def test_get_term_students_nonexisting(
    client: TestClient, superuser_token_headers: Dict[str, str], db: Session
) -> None:
    r = client.get(f"{settings.API_V1_STR}/terms/{generate_uuid()}/students", headers=superuser_token_headers)
    assert r.status_code == 404


def test_add_term_students_nonexisting(
    client: TestClient, superuser_token_headers: Dict[str, str], db: Session
) -> None:
    last_term_id = sorted(term.id for term in crud.term.get_multi(db))[-1]
    term = crud.term.get(db, id=last_term_id)
    assert term
    students = [
        create_random_user(db, type="student", school_id=term.year.school_id),
        create_random_user(db, type="student", school_id=term.year.school_id),
    ]
    data = [user.id for user in students]
    r = client.post(
        f"{settings.API_V1_STR}/terms/{generate_uuid()}/students", headers=superuser_token_headers, json=data
    )
    assert r.status_code == 404


def test_add_term_students_not_a_user(client: TestClient, superuser_token_headers: Dict[str, str], db: Session) -> None:
    term = create_random_term(db)
    students = [
        create_random_user(db, type="student", school_id=term.year.school_id),
        create_random_user(db, type="student", school_id=term.year.school_id),
    ]
    data = [user.id for user in students]
    new_user_id = generate_uuid()
    data.append(new_user_id)
    r = client.post(f"{settings.API_V1_STR}/terms/{term.id}/students", headers=superuser_token_headers, json=data)
    assert r.status_code == 207
    response = r.json()
    assert response.get("errors").get("not a user")[0] == new_user_id
    for user in students:
        student = crud.student.get(db, id=user.id)
        assert student
        assert student.user_id in response.get("success")
        assert student.term_id == term.id


def test_add_term_students_not_a_student(
    client: TestClient, superuser_token_headers: Dict[str, str], db: Session
) -> None:
    term = create_random_term(db)
    students = [
        create_random_user(db, type="student", school_id=term.year.school_id),
        create_random_user(db, type="student", school_id=term.year.school_id),
    ]
    data = [user.id for user in students]
    non_student = create_random_user(db, type="professor", school_id=term.year.school_id)
    data.append(non_student.id)
    r = client.post(f"{settings.API_V1_STR}/terms/{term.id}/students", headers=superuser_token_headers, json=data)
    assert r.status_code == 207
    response = r.json()
    assert response.get("errors").get("not a student")[0] == non_student.id
    for user in students:
        student = crud.student.get(db, id=user.id)
        assert student
        assert student.user_id in response.get("success")
        assert student.term_id == term.id


def test_add_term_students_different_school(
    client: TestClient, superuser_token_headers: Dict[str, str], db: Session
) -> None:
    term = create_random_term(db)
    students = [
        create_random_user(db, type="student", school_id=term.year.school_id),
        create_random_user(db, type="student", school_id=term.year.school_id),
    ]
    data = [user.id for user in students]
    student_different_school = create_random_user(db, type="student", school_id=create_random_school(db).id)
    data.append(student_different_school.id)
    r = client.post(f"{settings.API_V1_STR}/terms/{term.id}/students", headers=superuser_token_headers, json=data)
    assert r.status_code == 207
    response = r.json()
    assert response.get("errors").get("different schools")[0] == student_different_school.id
    for user in students:
        student = crud.student.get(db, id=user.id)
        assert student
        assert student.user_id in response.get("success")
        assert student.term_id == term.id


def test_add_term_students_no_student_object(
    client: TestClient, superuser_token_headers: Dict[str, str], db: Session
) -> None:
    term = create_random_term(db)
    students = [
        create_random_user(db, type="student", school_id=term.year.school_id),
        create_random_user(db, type="student", school_id=term.year.school_id),
    ]
    data = [user.id for user in students]
    student_no_object = create_random_user(db, type="student", school_id=term.year.school_id)
    crud.student.remove(db, id=student_no_object.id)
    data.append(student_no_object.id)
    r = client.post(f"{settings.API_V1_STR}/terms/{term.id}/students", headers=superuser_token_headers, json=data)
    assert r.status_code == 207
    response = r.json()
    assert response.get("errors").get("no student object")[0] == student_no_object.id
    for user in students:
        student = crud.student.get(db, id=user.id)
        assert student
        assert student.user_id in response.get("success")
        assert student.term_id == term.id


def test_add_term_students_duplicate(client: TestClient, superuser_token_headers: Dict[str, str], db: Session) -> None:
    term = create_random_term(db)
    s = create_random_user(db, type="student", school_id=term.year.school_id)
    students = [s, s]
    data = [user.id for user in students]
    r = client.post(f"{settings.API_V1_STR}/terms/{term.id}/students", headers=superuser_token_headers, json=data)
    assert r.status_code == 207
    assert r.json()
    assert s.id in [student_id for student_id in r.json()["success"]]
    student = crud.student.get(db, id=s.id)
    assert student
    assert student.term_id == term.id
    assert s.id in [student_id for student_id in r.json().get("errors").get("student already in term")]


def test_add_term_students(client: TestClient, superuser_token_headers: Dict[str, str], db: Session) -> None:
    term = create_random_term(db)
    students = [
        create_random_user(db, type="student", school_id=term.year.school_id),
        create_random_user(db, type="student", school_id=term.year.school_id),
    ]
    data = [user.id for user in students]
    r = client.post(f"{settings.API_V1_STR}/terms/{term.id}/students", headers=superuser_token_headers, json=data)
    assert r.status_code == 207
    assert r.json()
    fetched_students = [student_id for student_id in r.json()["success"]]
    for user in students:
        assert user.id in fetched_students
        student = crud.student.get(db, id=user.id)
        assert student
        assert student.term_id == term.id


def test_remove_term_student(client: TestClient, superuser_token_headers: Dict[str, str], db: Session) -> None:
    term = create_random_term(db)
    students = [
        create_random_user(db, type="student", school_id=term.year.school_id),
        create_random_user(db, type="student", school_id=term.year.school_id),
    ]
    for user in students:
        student = crud.student.get(db, user.id)
        assert student
        crud.student.update(db, db_obj=student, obj_in=StudentUpdate(term_id=term.id))
    r = client.delete(
        f"{settings.API_V1_STR}/terms/{term.id}/students/{students[0].id}", headers=superuser_token_headers
    )
    assert r.status_code == 200
    updated_student = r.json()
    assert updated_student["user_id"] == students[0].id
    assert updated_student["term_id"] is None


def test_remove_nonexisting_term_student(
    client: TestClient, superuser_token_headers: Dict[str, str], db: Session
) -> None:
    r = client.delete(
        f"{settings.API_V1_STR}/terms/{generate_uuid()}/students/{generate_uuid()}", headers=superuser_token_headers
    )
    assert r.status_code == 404


def test_remove_term_nonexisting_student(
    client: TestClient, superuser_token_headers: Dict[str, str], db: Session
) -> None:
    term = create_random_term(db)
    r = client.delete(
        f"{settings.API_V1_STR}/terms/{term.id}/students/{generate_uuid()}", headers=superuser_token_headers
    )
    assert r.status_code == 404


def test_create_term(client: TestClient, superuser_token_headers: Dict[str, str], db: Session) -> None:
    name = random_lower_string()
    year_id = create_random_year(db=db).id
    start_date = datetime.now().date()
    end_date = start_date + timedelta(days=90)
    current_year_term = randint(1, 4)
    has_electives = choice([True, False])
    data = {
        "name": name,
        "year_id": year_id,
        "start_date": start_date.isoformat(),
        "end_date": end_date.isoformat(),
        "current_year_term": current_year_term,
        "has_electives": has_electives,
    }
    r = client.post(f"{settings.API_V1_STR}/terms/", headers=superuser_token_headers, json=data)
    assert r.status_code == 200
    created_term = r.json()
    fetched_term = crud.term.get_by_details(
        db=db,
        name=name,
        year_id=year_id,
        current_year_term=current_year_term,
        start_date=start_date,
        end_date=end_date,
    )
    assert fetched_term
    compare_api_and_db_query_results(api_result=created_term, db_dict=to_json(fetched_term))
    compare_api_and_db_query_results(data, created_term)


def test_create_term_existing(client: TestClient, superuser_token_headers: Dict[str, str], db: Session) -> None:
    term = create_random_term(db=db)
    data = {
        "name": term.name,
        "year_id": term.year_id,
        "start_date": term.start_date.isoformat(),
        "end_date": term.end_date.isoformat() if term.end_date else None,
        "current_year_term": term.current_year_term,
        "has_electives": term.has_electives,
    }
    r = client.post(f"{settings.API_V1_STR}/terms/", headers=superuser_token_headers, json=data)
    assert r.status_code == 409


def test_get_term_normal_user(client: TestClient, normal_user_token_headers: Dict[str, str], db: Session) -> None:
    r = client.get(f"{settings.API_V1_STR}/terms/", headers=normal_user_token_headers)
    assert r.status_code == 403


def test_update_term_nonexisting(client: TestClient, superuser_token_headers: Dict[str, str], db: Session) -> None:
    r = client.put(f"{settings.API_V1_STR}/terms/{generate_uuid()}", headers=superuser_token_headers, json={})
    assert r.status_code == 404


def test_update_term(client: TestClient, superuser_token_headers: Dict[str, str], db: Session) -> None:
    term = create_random_term(db=db)
    assert term.start_date
    assert term.end_date
    start_date = term.start_date - timedelta(days=6 * 30)
    end_date = term.end_date - timedelta(days=6 * 30)
    data = {
        "start_date": start_date.isoformat(),
        "end_date": end_date.isoformat(),
        "is_active": not term.is_active,
    }
    r = client.put(f"{settings.API_V1_STR}/terms/{term.id}", headers=superuser_token_headers, json=data)
    fetched_term = r.json()
    db.refresh(term)
    assert fetched_term
    compare_api_and_db_query_results(api_result=fetched_term, db_dict=to_json(term))


def test_delete_term(client: TestClient, superuser_token_headers: Dict[str, str], db: Session) -> None:
    term = create_random_term(db=db)
    r = client.delete(f"{settings.API_V1_STR}/terms/{term.id}", headers=superuser_token_headers)
    assert r.status_code == 200
    deleted_term = crud.term.get(db=db, id=term.id)
    assert deleted_term is None


def test_delete_term_nonexisting(client: TestClient, superuser_token_headers: Dict[str, str], db: Session) -> None:
    r = client.delete(f"{settings.API_V1_STR}/terms/{generate_uuid()}", headers=superuser_token_headers)
    assert r.status_code == 404
