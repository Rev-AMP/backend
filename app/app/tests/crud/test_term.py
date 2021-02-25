from datetime import datetime, timedelta

from sqlalchemy.orm import Session

from app import crud
from app.tests.utils.term import create_random_term
from app.tests.utils.utils import random_lower_string


def test_create_inactive_term(db: Session) -> None:
    name = random_lower_string()
    start_date = datetime.now().date()
    end_date = (datetime.now() + timedelta(days=90)).date()
    term = create_random_term(db=db, name=name, start_date=start_date, end_date=end_date, is_active=False)
    assert term
    assert term.name == name
    assert term.start_date == start_date
    assert term.end_date == end_date
    assert not term.is_active


def test_get_by_year_term(db: Session) -> None:
    term = create_random_term(db=db)
    assert term.year_id
    assert term.current_year_term
    fetched_term = crud.term.get_by_year_term(db=db, year_id=term.year_id, current_year_term=term.current_year_term)[-1]
    assert fetched_term
    assert fetched_term.id == term.id


def test_get_by_name(db: Session) -> None:
    term = create_random_term(db=db)
    assert term.name
    fetched_term = crud.term.get_by_name(db=db, name=term.name)[-1]
    assert fetched_term
    assert fetched_term.id == term.id


def test_get_by_year(db: Session) -> None:
    term = create_random_term(db=db)
    assert term.year_id
    fetched_term = crud.term.get_by_year(db=db, year_id=term.year_id)[-1]
    assert fetched_term
    assert fetched_term.id == term.id


def test_get_by_start_date(db: Session) -> None:
    term = create_random_term(db=db)
    assert term.start_date
    fetched_term = crud.term.get_by_start(db=db, start_date=term.start_date)[-1]
    assert fetched_term
    assert fetched_term.id == term.id


def test_get_by_end_date(db: Session) -> None:
    term = create_random_term(db=db)
    assert term.end_date
    fetched_term = crud.term.get_by_end(db=db, end_date=term.end_date)[-1]
    assert fetched_term
    assert fetched_term.id == term.id
