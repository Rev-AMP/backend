from random import randint

from sqlalchemy.orm import Session

from app import crud
from app.schemas import CourseUpdate
from app.tests.utils.course import create_random_course
from app.tests.utils.term import create_random_term
from app.tests.utils.utils import random_lower_string


def test_create_course(db: Session) -> None:
    name = random_lower_string()
    course_code = random_lower_string()[:20]
    panel_code = randint(1, 11)
    elective_code = random_lower_string()[:20]
    term_id = create_random_term(db).id
    course = create_random_course(
        db, name=name, course_code=course_code, panel_code=panel_code, elective_code=elective_code, term_id=term_id
    )
    assert course
    assert course.name == name
    assert course.course_code == course_code
    assert course.panel_code == panel_code
    assert course.elective_code == elective_code
    assert course.term_id == term_id


def test_update_course(db: Session) -> None:
    course = create_random_course(db)
    assert course
    name = random_lower_string()
    updated_course = crud.course.update(db, db_obj=course, obj_in=CourseUpdate(name=name))
    assert updated_course.name == name


def test_course_by_details(db: Session) -> None:
    course = create_random_course(db)
    assert course.name
    assert course.course_code
    assert course.panel_code
    assert course.term_id
    fetched_course = crud.course.get_by_details(
        db,
        name=course.name,
        course_code=course.course_code,
        panel_code=course.panel_code,
        term_id=course.term_id,
    )
    assert fetched_course
    assert fetched_course.id == course.id
