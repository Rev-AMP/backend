from datetime import datetime
from typing import Optional

from sqlalchemy.orm import Session

from app import crud
from app.models import Year
from app.schemas import YearCreate
from app.tests.utils.utils import random_lower_string

from .school import create_random_school

current_year = datetime.now().year


def create_random_year(
    db: Session,
    name: Optional[str] = None,
    school_id: Optional[int] = None,
    start_year: Optional[int] = None,
    end_year: Optional[int] = None,
    is_active: bool = True,
) -> Year:
    """
    Create a random school, or based on given inputs
    """

    if school_id is None:
        school_id = create_random_school(db).id

    return crud.year.create(
        db=db,
        obj_in=YearCreate(
            name=name or random_lower_string(),
            school_id=school_id,
            start_year=start_year or datetime.now().year,
            end_year=end_year or datetime.now().year + 1,
            is_active=is_active,
        ),
    )
