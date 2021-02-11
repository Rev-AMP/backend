from typing import Optional

from sqlalchemy.orm import Session

from app import crud
from app.models import School
from app.schemas import SchoolCreate
from app.tests.utils.utils import random_lower_string


def create_random_school(db: Session, name: Optional[str] = None, head: Optional[str] = None) -> School:
    """
    Create a random school, or based on given inputs
    """

    return crud.school.create(
        db=db, obj_in=SchoolCreate(name=name or random_lower_string(), head=head or random_lower_string())
    )
