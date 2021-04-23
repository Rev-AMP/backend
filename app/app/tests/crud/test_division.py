from random import randint

from sqlalchemy.orm import Session

from app import crud
from app.schemas import DivisionUpdate
from app.tests.utils.course import create_random_course
from app.tests.utils.division import create_random_division
from app.tests.utils.professor import create_random_professor
from app.tests.utils.student import create_random_student


def test_create_division(db: Session) -> None:
    course_id = create_random_course(db).id
    division_code = randint(1, 20)
    professor_id = create_random_professor(db).user_id
    division = create_random_division(db, course_id=course_id, division_code=division_code, professor_id=professor_id)
    assert division
    assert division.course_id == course_id
    assert division.division_code == division_code
    assert division.professor_id == professor_id


def test_update_division(db: Session) -> None:
    professor_id = create_random_professor(db).user_id
    division = create_random_division(db)
    assert division
    updated_division = crud.division.update(db, db_obj=division, obj_in=DivisionUpdate(professor_id=professor_id))
    assert updated_division.professor_id == professor_id


def test_division_by_details(db: Session) -> None:
    division = create_random_division(db)
    assert division.course_id
    assert division.division_code
    fetched_division = crud.division.get_by_details(
        db,
        course_id=division.course_id,
        division_code=division.division_code,
    )
    assert fetched_division
    assert fetched_division.id == division.id


def test_add_students_to_division(db: Session) -> None:
    division = create_random_division(db)
    assert division
    students = [
        create_random_student(db, term_id=division.course.term_id),
        create_random_student(db, term_id=division.course.term_id),
    ]
    random_batch = randint(1, 5)
    for student in students:
        division.students.append({"student": student, "batch_number": random_batch})
    db.commit()
    for student in students:
        db.refresh(student)
        assert student.divisions
        assert student.divisions[0] == division


def test_add_students_to_division_batches(db: Session) -> None:
    division = create_random_division(db)
    assert division
    students = [
        create_random_student(db, term_id=division.course.term_id),
        create_random_student(db, term_id=division.course.term_id),
    ]
    random_batch = randint(1, 5)
    for student in students:
        division.students.append({"student": student, "batch_number": random_batch})
    db.commit()
    for student in students:
        db.refresh(student)
        assert student.divisions
        assert student.divisions[0] == division
        assert getattr(student, "student_division")[0].division_id == division.id
        assert getattr(student, "student_division")[0].batch_number == random_batch
