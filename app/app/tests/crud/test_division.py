from random import randint

from sqlalchemy.orm import Session

from app import crud
from app.schemas import DivisionUpdate
from app.tests.utils.course import create_random_course
from app.tests.utils.division import create_random_division
from app.tests.utils.professor import create_random_professor


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
    division = create_random_division(db)
    assert division
    professor_id = create_random_professor(db).user_id
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
