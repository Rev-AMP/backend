from random import randint
from typing import Dict

from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app import crud
from app.core.config import settings
from app.schemas import AdminPermissions
from app.tests.utils.course import create_random_course
from app.tests.utils.division import create_random_division
from app.tests.utils.student import create_random_student
from app.tests.utils.term import create_random_term
from app.tests.utils.user import authentication_token_from_email, create_random_user
from app.tests.utils.utils import compare_api_and_db_query_results, to_json
from app.utils import generate_uuid


def test_get_students_superuser(client: TestClient, superuser_token_headers: Dict[str, str], db: Session) -> None:
    create_random_student(db)
    create_random_student(db)
    r = client.get(
        f"{settings.API_V1_STR}/students/",
        headers=superuser_token_headers,
    )
    assert r.status_code == 200
    all_students = r.json()
    assert len(all_students) >= 2
    for student in all_students:
        assert "user_id" in student
        assert "term_id" in student


def test_get_students_normal_user(client: TestClient, normal_user_token_headers: Dict[str, str], db: Session) -> None:
    create_random_student(db)
    create_random_student(db)
    r = client.get(
        f"{settings.API_V1_STR}/students/",
        headers=normal_user_token_headers,
    )
    assert r.status_code == 403


def test_update_students_non_admin(client: TestClient, db: Session) -> None:
    student = create_random_student(db)
    term_id = create_random_term(db).id
    data = {"term_id": term_id}
    r = client.put(
        f"{settings.API_V1_STR}/students/{student.user_id}",
        headers=authentication_token_from_email(client=client, email=student.user.email, db=db),
        json=data,
    )
    assert r.status_code == 403


def test_update_nonexisting_student(client: TestClient, superuser_token_headers: Dict[str, str], db: Session) -> None:
    term_id = create_random_term(db).id
    data = {"term_id": term_id}
    r = client.put(
        f"{settings.API_V1_STR}/students/{generate_uuid()}",
        headers=superuser_token_headers,
        json=data,
    )
    assert r.status_code == 404


def test_update_students_superuser(client: TestClient, superuser_token_headers: Dict[str, str], db: Session) -> None:
    student = create_random_student(db)
    term_id = create_random_term(db).id
    data = {"term_id": term_id}
    r = client.put(
        f"{settings.API_V1_STR}/students/{student.user_id}",
        headers=superuser_token_headers,
        json=data,
    )
    assert r.status_code == 200
    updated_student = r.json()
    assert updated_student
    db.refresh(student)
    compare_api_and_db_query_results(api_result=updated_student, db_dict=to_json(student))


def test_get_student_me_superuser(client: TestClient, superuser_token_headers: Dict[str, str], db: Session) -> None:
    r = client.get(
        f"{settings.API_V1_STR}/students/me",
        headers=superuser_token_headers,
    )
    assert r.status_code == 403


def test_get_student_me_normal_student(client: TestClient, db: Session) -> None:
    student = create_random_student(db)
    r = client.get(
        f"{settings.API_V1_STR}/students/me",
        headers=authentication_token_from_email(client=client, email=student.user.email, db=db),
    )
    assert r.status_code == 200
    fetched_student = r.json()
    assert fetched_student
    compare_api_and_db_query_results(api_result=fetched_student, db_dict=to_json(student))


def test_get_student_id(client: TestClient, db: Session) -> None:
    student = create_random_student(db)
    r = client.get(
        f"{settings.API_V1_STR}/students/{student.user_id}",
        headers=authentication_token_from_email(client=client, email=student.user.email, db=db),
    )
    assert r.status_code == 200
    fetched_student = r.json()
    assert fetched_student
    db.refresh(student)
    compare_api_and_db_query_results(api_result=fetched_student, db_dict=to_json(student))


def test_get_nonexistent_student(client: TestClient, superuser_token_headers: Dict[str, str], db: Session) -> None:
    r = client.get(
        f"{settings.API_V1_STR}/students/{generate_uuid()}",
        headers=superuser_token_headers,
    )
    assert r.status_code == 404


def test_get_student_from_student(client: TestClient, normal_user_token_headers: Dict[str, str], db: Session) -> None:
    user_id = sorted([student.user_id for student in crud.student.get_multi(db)])[-1]
    r = client.get(
        f"{settings.API_V1_STR}/students/{user_id}",
        headers=normal_user_token_headers,
    )
    assert r.status_code == 403


def test_get_student_me_normal_user(client: TestClient, db: Session) -> None:
    student = create_random_student(db)
    r = client.get(
        f"{settings.API_V1_STR}/students/me",
        headers=authentication_token_from_email(client=client, email=student.user.email, db=db),
    )
    assert r.status_code == 200
    fetched_student = r.json()
    assert fetched_student
    compare_api_and_db_query_results(api_result=fetched_student, db_dict=to_json(student))


def test_read_student_by_id_superuser(client: TestClient, superuser_token_headers: Dict[str, str], db: Session) -> None:
    student = create_random_student(db)
    r = client.get(
        f"{settings.API_V1_STR}/students/{student.user_id}",
        headers=superuser_token_headers,
    )
    assert r.status_code == 200
    fetched_student = r.json()
    assert fetched_student
    compare_api_and_db_query_results(api_result=fetched_student, db_dict=to_json(student))


def test_get_student_divisions_id(client: TestClient, db: Session) -> None:
    student = create_random_student(db)
    course = create_random_course(db, term_id=student.term_id)
    divisions = [create_random_division(db, course_id=course.id), create_random_division(db, course_id=course.id)]
    batch_number = randint(1, 5)
    for division in divisions:
        division.students.append({"student": student, "batch_number": batch_number})
    r = client.get(
        f"{settings.API_V1_STR}/students/{student.user_id}/divisions",
        headers=authentication_token_from_email(client=client, email=student.user.email, db=db),
    )
    assert r.status_code == 200
    fetched_divisions = r.json()
    assert fetched_divisions
    assert len(fetched_divisions) == 2
    for division in divisions:
        if fetched_divisions[0].get("id") == division.id:
            compare_api_and_db_query_results(api_result=fetched_divisions[0], db_dict=to_json(division))
        else:
            compare_api_and_db_query_results(api_result=fetched_divisions[1], db_dict=to_json(division))
    # assert division.id == fetched_divisions[0].get("id") or division.id == fetched_divisions[1].get("id")


def test_get_student_divisions_id_admin_with_perms(client: TestClient, db: Session) -> None:
    student = create_random_student(db)
    course = create_random_course(db, term_id=student.term_id)
    division = create_random_division(db, course_id=course.id)
    division.students.append({"student": student, "batch_number": randint(1, 5)})

    perms = AdminPermissions(0)
    perms["student"] = True
    admin = create_random_user(db, type="admin", permissions=perms.permissions)

    r = client.get(
        f"{settings.API_V1_STR}/students/{student.user_id}/divisions",
        headers=authentication_token_from_email(client=client, email=admin.email, db=db),
    )
    assert r.status_code == 200
    fetched_divisions = r.json()
    assert fetched_divisions
    # compare_api_and_db_query_results(api_result=fetched_divisions[0], db_dict=to_json(division))
    assert division.id == fetched_divisions[0].get("id")


def test_get_student_divisions_id_admin_without_perms(client: TestClient, db: Session) -> None:
    student = create_random_student(db)
    admin = create_random_user(db, type="admin")
    r = client.get(
        f"{settings.API_V1_STR}/students/{student.user_id}/divisions",
        headers=authentication_token_from_email(client=client, email=admin.email, db=db),
    )
    assert r.status_code == 403


def test_get_student_divisions_id_normal_user(
    client: TestClient, normal_user_token_headers: Dict[str, str], db: Session
) -> None:
    student = create_random_student(db)
    course = create_random_course(db, term_id=student.term_id)
    division = create_random_division(db, course_id=course.id)
    division.students.append({"student": student, "batch_number": randint(1, 5)})
    r = client.get(
        f"{settings.API_V1_STR}/students/{student.user_id}/divisions",
        headers=normal_user_token_headers,
    )
    assert r.status_code == 403


def test_get_student_divisions_id_nonexistent(
    client: TestClient, normal_user_token_headers: Dict[str, str], db: Session
) -> None:
    r = client.get(
        f"{settings.API_V1_STR}/students/{generate_uuid()}/divisions",
        headers=normal_user_token_headers,
    )
    assert r.status_code == 404


def test_get_student_me_divisions(client: TestClient, db: Session) -> None:
    student = create_random_student(db)
    course = create_random_course(db, term_id=student.term_id)
    divisions = [create_random_division(db, course_id=course.id), create_random_division(db, course_id=course.id)]
    batch_number = randint(1, 5)
    for division in divisions:
        division.students.append({"student": student, "batch_number": batch_number})
    r = client.get(
        f"{settings.API_V1_STR}/students/me/divisions",
        headers=authentication_token_from_email(client=client, email=student.user.email, db=db),
    )
    assert r.status_code == 200
    fetched_divisions = r.json()
    assert fetched_divisions
    assert len(fetched_divisions) == 2
    for division in divisions:
        if fetched_divisions[0].get("id") == division.id:
            compare_api_and_db_query_results(api_result=fetched_divisions[0], db_dict=to_json(division))
        else:
            compare_api_and_db_query_results(api_result=fetched_divisions[1], db_dict=to_json(division))
        # assert division.id == fetched_divisions[0].get("id") or division.id == fetched_divisions[1].get("id")


def test_get_student_me_divisions_superuser(
    client: TestClient, superuser_token_headers: Dict[str, str], db: Session
) -> None:
    r = client.get(f"{settings.API_V1_STR}/students/me/divisions", headers=superuser_token_headers)
    assert r.status_code == 403
