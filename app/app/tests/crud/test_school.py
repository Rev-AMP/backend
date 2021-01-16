from sqlalchemy.orm import Session

from app import crud
from app.schemas import SchoolUpdate
from app.tests.utils.school import create_random_school
from app.tests.utils.utils import random_lower_string


def test_create_school(db: Session) -> None:
    name = random_lower_string()
    head = random_lower_string()
    school = create_random_school(db=db, name=name, head=head)
    assert school
    assert school.name == name
    assert school.head == head


def test_update_school(db: Session) -> None:
    school = create_random_school(db)
    name = random_lower_string()
    school_in = SchoolUpdate(name=name)
    school = crud.school.update(db=db, db_obj=school, obj_in=school_in)
    assert school
    assert school.name == name
