from datetime import datetime, timedelta

from sqlalchemy.orm import Session

from app.tests.utils.term import create_random_term
from app.tests.utils.utils import random_lower_string


def create_test_inactive_term(db: Session) -> None:
    name = random_lower_string()
    start_date = datetime.now().date()
    end_date = (datetime.now() + timedelta(days=90)).date()
    term = create_random_term(db=db, name=name, start_date=start_date, end_date=end_date, is_active=False)
    assert term
    assert term.name == name
    assert term.start_date == start_date
    assert term.end_date == end_date
    assert not term.is_active
