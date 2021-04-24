import logging
from random import randint
from typing import Dict

from sqlalchemy import exc
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
from app.tests.utils.school import create_random_school
from app.tests.utils.student import create_random_student
from app.tests.utils.term import create_random_term
from app.tests.utils.user import authentication_token_from_email, create_random_user
from app.tests.utils.utils import compare_api_and_db_query_results, to_json
from app.utils import generate_uuid


def test_get_all_divisions(client: TestClient, superuser_token_headers: Dict[str, str], db: Session) -> None:
    division = create_random_division(db)
    r = client.get(f"{settings.API_V1_STR}/divisions/", headers=superuser_token_headers)
    assert r.status_code == 200
    results = r.json()
    assert results
    compare_api_and_db_query_results(results[-1], to_json(division))


def test_get_division_existing(client: TestClient, superuser_token_headers: Dict[str, str], db: Session) -> None:
    division = create_random_division(db)
    r = client.get(f"{settings.API_V1_STR}/divisions/{division.id}", headers=superuser_token_headers)
    assert r.status_code == 200
    fetched_division = r.json()
    assert fetched_division
    compare_api_and_db_query_results(fetched_division, to_json(division))


def test_get_division_nonexisting(client: TestClient, superuser_token_headers: Dict[str, str], db: Session) -> None:
    r = client.get(f"{settings.API_V1_STR}/divisions/{generate_uuid()}", headers=superuser_token_headers)
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
    compare_api_and_db_query_results(created_division, to_json(fetched_division))
    compare_api_and_db_query_results(data, to_json(fetched_division))


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
    db.refresh(division)
    assert fetched_division
    compare_api_and_db_query_results(fetched_division, to_json(division))


def test_update_division_nonexisting(client: TestClient, superuser_token_headers: Dict[str, str], db: Session) -> None:
    r = client.put(f"{settings.API_V1_STR}/divisions/{generate_uuid()}", headers=superuser_token_headers, json={})
    assert r.status_code == 404


def test_delete_division(client: TestClient, superuser_token_headers: Dict[str, str], db: Session) -> None:
    division = create_random_division(db)
    r = client.delete(f"{settings.API_V1_STR}/divisions/{division.id}", headers=superuser_token_headers)
    assert r.status_code == 200
    deleted_division = crud.division.get(db, id=division.id)
    assert deleted_division is None


def test_delete_division_nonexisting(client: TestClient, superuser_token_headers: Dict[str, str], db: Session) -> None:
    r = client.delete(f"{settings.API_V1_STR}/divisions/{generate_uuid()}", headers=superuser_token_headers)
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


def test_add_division_students_not_a_user(
    client: TestClient, superuser_token_headers: Dict[str, str], db: Session
) -> None:
    division = create_random_division(db)
    new_user_id = generate_uuid()
    data = [new_user_id]
    r = client.post(
        f"{settings.API_V1_STR}/divisions/{division.id}/students", headers=superuser_token_headers, json=data
    )
    assert r.status_code == 207
    response = r.json()
    assert response.get("errors").get("not a user")[0] == new_user_id


def test_add_division_students_not_a_student(
    client: TestClient, superuser_token_headers: Dict[str, str], db: Session
) -> None:
    course = create_random_course(db)
    division = create_random_division(db, course_id=course.id)
    students = [
        create_random_student(db, school_id=course.term.year.school_id, term_id=course.term_id),
        create_random_student(db, school_id=course.term.year.school_id, term_id=course.term_id),
    ]
    data = [student.user_id for student in students]
    non_student = create_random_user(db, type="professor", school_id=division.course.term.year.school_id)
    data.append(non_student.id)
    r = client.post(
        f"{settings.API_V1_STR}/divisions/{division.id}/students", headers=superuser_token_headers, json=data
    )
    assert r.status_code == 207
    response = r.json()
    assert response.get("errors").get("not a student")[0] == non_student.id
    for student in students:
        assert student.user_id in response.get("success")


def test_add_division_students_different_school(
    client: TestClient, superuser_token_headers: Dict[str, str], db: Session
) -> None:
    course = create_random_course(db)
    division = create_random_division(db, course_id=course.id)
    students = [
        create_random_student(db, school_id=course.term.year.school_id, term_id=course.term_id),
        create_random_student(db, school_id=course.term.year.school_id, term_id=course.term_id),
    ]
    data = [student.user_id for student in students]
    student_different_school = create_random_user(db, type="student", school_id=create_random_school(db).id)
    data.append(student_different_school.id)
    r = client.post(
        f"{settings.API_V1_STR}/divisions/{division.id}/students", headers=superuser_token_headers, json=data
    )
    assert r.status_code == 207
    response = r.json()
    assert response.get("errors").get("different schools")[0] == student_different_school.id
    for student in students:
        assert student.user_id in response.get("success")


def test_add_division_students_different_term(
    client: TestClient, superuser_token_headers: Dict[str, str], db: Session
) -> None:
    course = create_random_course(db)
    division = create_random_division(db, course_id=course.id)
    students = [
        create_random_student(db, school_id=course.term.year.school_id, term_id=course.term_id),
        create_random_student(db, school_id=course.term.year.school_id, term_id=course.term_id),
    ]
    data = [student.user_id for student in students]
    student_different_term = create_random_student(
        db, school_id=course.term.year.school_id, term_id=create_random_term(db).id
    )
    data.append(student_different_term.user_id)
    r = client.post(
        f"{settings.API_V1_STR}/divisions/{division.id}/students", headers=superuser_token_headers, json=data
    )
    assert r.status_code == 207
    response = r.json()
    assert response.get("errors").get("different terms")[0] == student_different_term.user_id
    for student in students:
        assert student.user_id in response.get("success")


def test_add_division_students_no_student_object(
    client: TestClient, superuser_token_headers: Dict[str, str], db: Session
) -> None:
    course = create_random_course(db)
    division = create_random_division(db, course_id=course.id)
    students = [
        create_random_student(db, school_id=course.term.year.school_id, term_id=course.term_id),
        create_random_student(db, school_id=course.term.year.school_id, term_id=course.term_id),
    ]
    data = [student.user_id for student in students]
    student_no_object = create_random_student(db, school_id=course.term.year.school_id, term_id=course.term_id)
    crud.student.remove(db, id=student_no_object.user_id)
    data.append(student_no_object.user_id)
    r = client.post(
        f"{settings.API_V1_STR}/divisions/{division.id}/students", headers=superuser_token_headers, json=data
    )
    assert r.status_code == 207
    response = r.json()
    assert response.get("errors").get("no student object")[0] == student_no_object.user_id
    for student in students:
        assert student.user_id in response.get("success")


def test_add_division_students_non_existent_division(
    client: TestClient, superuser_token_headers: Dict[str, str], db: Session
) -> None:
    r = client.post(
        f"{settings.API_V1_STR}/divisions/{generate_uuid()}/students", headers=superuser_token_headers, json=[]
    )
    assert r.status_code == 404


def test_add_division_students(client: TestClient, superuser_token_headers: Dict[str, str], db: Session) -> None:
    course = create_random_course(db)
    division = create_random_division(db, course_id=course.id)
    students = [
        create_random_student(db, school_id=course.term.year.school_id, term_id=course.term_id),
        create_random_student(db, school_id=course.term.year.school_id, term_id=course.term_id),
    ]
    data = [student.user_id for student in students]
    r = client.post(
        f"{settings.API_V1_STR}/divisions/{division.id}/students", headers=superuser_token_headers, json=data
    )
    assert r.status_code == 207
    assert r.json()
    fetched_students = [student_id for student_id in r.json()["success"]]
    for student in students:
        assert student.user_id in fetched_students


def test_get_division_students(client: TestClient, superuser_token_headers: Dict[str, str], db: Session) -> None:
    course = create_random_course(db)
    division = create_random_division(db, course_id=course.id)
    students = [
        create_random_student(db, school_id=course.term.year.school_id, term_id=course.term_id),
        create_random_student(db, school_id=course.term.year.school_id, term_id=course.term_id),
    ]
    batch_number = randint(1, 5)
    for student in students:
        division.students.append({"student": student, "batch_number": batch_number})
    try:
        db.commit()
    except exc.IntegrityError as e:
        logging.error(e.__str__())
        db.rollback()
    except Exception as e:
        logging.error(e.__str__())
        db.rollback()
    r = client.get(f"{settings.API_V1_STR}/divisions/{division.id}/students", headers=superuser_token_headers)
    assert r.status_code == 200
    assert r.json()
    fetched_students = [student.get("user_id") for student in r.json()]
    for student in students:
        assert student.user_id in fetched_students


def test_get_division_students_professor(client: TestClient, db: Session) -> None:
    course = create_random_course(db)
    professor = create_random_user(db, type="professor", school_id=course.term.year.school_id)
    division = create_random_division(db, course_id=course.id, professor_id=professor.id)
    students = [
        create_random_student(db, school_id=course.term.year.school_id, term_id=course.term_id),
        create_random_student(db, school_id=course.term.year.school_id, term_id=course.term_id),
    ]
    batch_number = randint(1, 5)
    for student in students:
        division.students.append({"student": student, "batch_number": batch_number})
    try:
        db.commit()
    except exc.IntegrityError as e:
        logging.error(e.__str__())
        db.rollback()
    except Exception as e:
        logging.error(e.__str__())
        db.rollback()
    r = client.get(
        f"{settings.API_V1_STR}/divisions/{division.id}/students",
        headers=authentication_token_from_email(client=client, db=db, email=professor.email),
    )
    assert r.status_code == 200
    assert r.json()
    fetched_students = [student.get("user_id") for student in r.json()]
    for student in students:
        assert student.user_id in fetched_students


def test_get_division_students_admin_with_perms(client: TestClient, db: Session) -> None:
    course = create_random_course(db)
    division = create_random_division(db, course_id=course.id)
    students = [
        create_random_student(db, school_id=course.term.year.school_id, term_id=course.term_id),
        create_random_student(db, school_id=course.term.year.school_id, term_id=course.term_id),
    ]
    batch_number = randint(1, 5)
    for student in students:
        division.students.append({"student": student, "batch_number": batch_number})
    try:
        db.commit()
    except exc.IntegrityError as e:
        logging.error(e.__str__())
        db.rollback()
    except Exception as e:
        logging.error(e.__str__())
        db.rollback()
    perms = AdminPermissions(0)
    perms["course"] = True
    admin = create_random_user(db, type="admin", permissions=perms.permissions)
    r = client.get(
        f"{settings.API_V1_STR}/divisions/{division.id}/students",
        headers=authentication_token_from_email(client=client, db=db, email=admin.email),
    )
    assert r.status_code == 200
    assert r.json()
    fetched_students = [student.get("user_id") for student in r.json()]
    for student in students:
        assert student.user_id in fetched_students


def test_get_division_students_admin_without_perms(
    client: TestClient, admin_user_token_headers: Dict[str, str], db: Session
) -> None:
    division = create_random_division(db)
    r = client.get(
        f"{settings.API_V1_STR}/divisions/{division.id}/students",
        headers=admin_user_token_headers,
    )
    assert r.status_code == 403


def test_get_division_students_normal_user(
    client: TestClient, normal_user_token_headers: Dict[str, str], db: Session
) -> None:
    division = create_random_division(db)
    r = client.get(
        f"{settings.API_V1_STR}/divisions/{division.id}/students",
        headers=normal_user_token_headers,
    )
    assert r.status_code == 403


def test_get_division_students_non_existent_division(
    client: TestClient, normal_user_token_headers: Dict[str, str], db: Session
) -> None:
    r = client.get(
        f"{settings.API_V1_STR}/divisions/{generate_uuid()}/students",
        headers=normal_user_token_headers,
    )
    assert r.status_code == 404


def test_get_division_batch_students(client: TestClient, superuser_token_headers: Dict[str, str], db: Session) -> None:
    course = create_random_course(db)
    division = create_random_division(db, course_id=course.id)
    students = [
        create_random_student(db, school_id=course.term.year.school_id, term_id=course.term_id),
        create_random_student(db, school_id=course.term.year.school_id, term_id=course.term_id),
    ]
    batch_number = randint(1, 5)
    for student in students:
        division.students.append({"student": student, "batch_number": batch_number})
    try:
        db.commit()
    except exc.IntegrityError as e:
        logging.error(e.__str__())
        db.rollback()
    except Exception as e:
        logging.error(e.__str__())
        db.rollback()
    r = client.get(
        f"{settings.API_V1_STR}/divisions/{division.id}/students/{batch_number}", headers=superuser_token_headers
    )
    assert r.status_code == 200
    student_ids = [student.get("user_id") for student in r.json()]
    for student in students:
        assert student.user_id in student_ids


def test_get_division_batch_students_professor(client: TestClient, db: Session) -> None:
    course = create_random_course(db)
    professor = create_random_user(db, type="professor", school_id=course.term.year.school_id)
    division = create_random_division(db, course_id=course.id, professor_id=professor.id)
    students = [
        create_random_student(db, school_id=course.term.year.school_id, term_id=course.term_id),
        create_random_student(db, school_id=course.term.year.school_id, term_id=course.term_id),
    ]
    batch_number = randint(1, 5)
    for student in students:
        division.students.append({"student": student, "batch_number": batch_number})
    try:
        db.commit()
    except exc.IntegrityError as e:
        logging.error(e.__str__())
        db.rollback()
    except Exception as e:
        logging.error(e.__str__())
        db.rollback()
    r = client.get(
        f"{settings.API_V1_STR}/divisions/{division.id}/students/{batch_number}",
        headers=authentication_token_from_email(client=client, db=db, email=professor.email),
    )
    assert r.status_code == 200
    student_ids = [student.get("user_id") for student in r.json()]
    for student in students:
        assert student.user_id in student_ids


def test_get_division_batch_students_admin_with_perms(client: TestClient, db: Session) -> None:
    course = create_random_course(db)
    division = create_random_division(db, course_id=course.id)
    students = [
        create_random_student(db, school_id=course.term.year.school_id, term_id=course.term_id),
        create_random_student(db, school_id=course.term.year.school_id, term_id=course.term_id),
    ]
    batch_number = randint(1, 5)
    for student in students:
        division.students.append({"student": student, "batch_number": batch_number})
    try:
        db.commit()
    except exc.IntegrityError as e:
        logging.error(e.__str__())
        db.rollback()
    except Exception as e:
        logging.error(e.__str__())
        db.rollback()
    perms = AdminPermissions(0)
    perms["course"] = True
    admin = create_random_user(db, type="admin", permissions=perms.permissions)
    r = client.get(
        f"{settings.API_V1_STR}/divisions/{division.id}/students/{batch_number}",
        headers=authentication_token_from_email(client=client, db=db, email=admin.email),
    )
    assert r.status_code == 200
    student_ids = [student.get("user_id") for student in r.json()]
    for student in students:
        assert student.user_id in student_ids


def test_get_division_batch_students_admin_without_perms(
    client: TestClient, admin_user_token_headers: Dict[str, str], db: Session
) -> None:
    division = create_random_division(db)
    r = client.get(
        f"{settings.API_V1_STR}/divisions/{division.id}/students/0",
        headers=admin_user_token_headers,
    )
    assert r.status_code == 403


def test_get_division_batch_students_normal_user(
    client: TestClient, normal_user_token_headers: Dict[str, str], db: Session
) -> None:
    division = create_random_division(db)
    r = client.get(
        f"{settings.API_V1_STR}/divisions/{division.id}/students/0",
        headers=normal_user_token_headers,
    )
    assert r.status_code == 403


def test_get_division_batch_students_non_existent_division(
    client: TestClient, normal_user_token_headers: Dict[str, str], db: Session
) -> None:
    r = client.get(
        f"{settings.API_V1_STR}/divisions/{generate_uuid()}/students/0",
        headers=normal_user_token_headers,
    )
    assert r.status_code == 404
