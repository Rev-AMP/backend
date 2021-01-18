from typing import Optional

from sqlalchemy.orm import Session

from app import crud
from app.models.school import School
from app.schemas import SchoolCreate
from app.tests.utils.utils import random_lower_string


def create_random_school(db: Session, name: Optional[str] = None, head: Optional[str] = None) -> School:
    """
    Create a random school, or based on given inputs
    """
    if not name:
        name = random_lower_string()

    if not head and head is not None:
        head = random_lower_string()

    school_in = SchoolCreate(name=name, head=head)
    school = crud.school.create(db=db, obj_in=school_in)

    return school
