from sqlalchemy.orm import Session

from app import crud
from app.schemas import CourseUpdate
from app.tests.utils.course import create_random_course
from app.tests.utils.utils import random_lower_string


def test_create_course(db: Session) -> None:
    name = random_lower_string()
    code = random_lower_string()[:20]
    course = create_random_course(db=db, name=name, code=code)
    assert course
    assert course.name == name
    assert course.code == code


def test_update_course(db: Session) -> None:
    course = create_random_course(db)
    assert course
    name = random_lower_string()
    updated_course = crud.course.update(db, db_obj=course, obj_in=CourseUpdate(name=name))
    assert updated_course.name == name


def test_course_by_details(db: Session) -> None:
    course = create_random_course(db)
    assert course.name
    assert course.code
    assert course.term_id
    fetched_course = crud.course.get_by_details(
        db,
        name=course.name,
        code=course.code,
        term_id=course.term_id,
    )
    assert fetched_course
    assert fetched_course.id == course.id


def test_course_by_name(db: Session) -> None:
    course = create_random_course(db)
    assert course.name
    fetched_course = crud.course.get_by_name(db, name=course.name)
    assert fetched_course
    assert fetched_course.id == course.id


def test_course_by_code(db: Session) -> None:
    course = create_random_course(db)
    assert course.code
    fetched_course = crud.course.get_by_code(db, code=course.code)
    assert fetched_course
    assert fetched_course.id == course.id


def test_course_by_term(db: Session) -> None:
    course = create_random_course(db)
    assert course.term_id
    fetched_course = crud.course.get_by_term(db, term_id=course.term_id)
    assert fetched_course
    assert fetched_course.id == course.id
