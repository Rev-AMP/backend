from datetime import datetime, timedelta
from random import randint

from sqlalchemy.orm import Session

from app import crud
from app.schemas import TermUpdate
from app.tests.utils.student import create_random_student
from app.tests.utils.term import create_random_term
from app.tests.utils.utils import random_lower_string


def test_create_term(db: Session) -> None:
    name = random_lower_string()
    start_date = datetime.now().date()
    end_date = (datetime.now() + timedelta(days=90)).date()
    term = create_random_term(db=db, name=name, start_date=start_date, end_date=end_date, is_active=False)
    assert term
    assert term.name == name
    assert term.start_date == start_date
    assert term.end_date == end_date
    assert not term.is_active


def test_update_term(db: Session) -> None:
    term = create_random_term(db=db, is_active=False)
    assert term
    end_date = term.start_date + timedelta(days=randint(2 * 30, 6 * 30))
    updated_term = crud.term.update(db=db, db_obj=term, obj_in=TermUpdate(end_date=end_date, is_active=True))
    assert updated_term.end_date == end_date
    assert updated_term.is_active


def test_get_by_details(db: Session) -> None:
    term = create_random_term(db=db)
    assert term.name
    assert term.year_id
    assert term.current_year_term
    assert term.start_date
    assert term.end_date
    fetched_term = crud.term.get_by_details(
        db=db,
        name=term.name,
        year_id=term.year_id,
        current_year_term=term.current_year_term,
        start_date=term.start_date,
        end_date=term.end_date,
    )
    assert fetched_term
    assert fetched_term.id == term.id


def test_get_students(db: Session) -> None:
    term = create_random_term(db)
    created_students = [create_random_student(db, term.id), create_random_student(db, term.id)]
    students = crud.term.get(db=db, id=term.id).students
    assert len(students) >= 2
    for student in students:
        assert student in created_students
