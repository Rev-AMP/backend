from datetime import date, datetime, timedelta
from random import randint
from typing import Optional

from sqlalchemy.orm import Session

from app import crud
from app.models import Term
from app.schemas import TermCreate

from .utils import random_lower_string
from .year import create_random_year


def create_random_term(
    db: Session,
    name: Optional[str] = None,
    year_id: Optional[int] = None,
    current_year_term: Optional[int] = None,
    start_date: Optional[date] = None,
    end_date: Optional[date] = None,
    has_electives: Optional[bool] = False,
    is_active: Optional[bool] = True,
) -> Term:
    """
    Create a random term, or based on given inputs
    """

    if year_id is None:
        year_id = create_random_year(db).id

    return crud.term.create(
        db=db,
        obj_in=TermCreate(
            name=name or random_lower_string(),
            year_id=year_id,
            current_year_term=current_year_term or randint(1, 4),
            start_date=start_date or datetime.now().date(),
            end_date=end_date or (datetime.now() + timedelta(days=90)).date(),
            has_electives=has_electives,
            is_active=is_active,
        ),
    )
