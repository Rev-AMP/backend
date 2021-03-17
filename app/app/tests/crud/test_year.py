from datetime import datetime

from sqlalchemy.orm import Session

from app import crud
from app.schemas import YearUpdate
from app.tests.utils.year import create_random_year


def test_create_year(db: Session) -> None:
    start_year = datetime.now().year
    end_year = start_year + 1
    year = create_random_year(db=db, start_year=start_year, end_year=end_year, is_active=False)
    assert year
    assert year.start_year == start_year
    assert year.end_year == end_year
    assert not year.is_active


def test_update_year(db: Session) -> None:
    start_year = datetime.now().year
    end_year = start_year + 1
    year = create_random_year(db=db, start_year=start_year, end_year=end_year, is_active=False)
    assert year
    updated_year = crud.year.update(db, db_obj=year, obj_in=YearUpdate(end_year=end_year + 1, is_active=True))
    assert updated_year.end_year == end_year + 1
    assert updated_year.is_active
