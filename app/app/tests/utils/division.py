from random import randint
from typing import Optional

from sqlalchemy.orm import Session

from app import crud
from app.models import Division
from app.schemas import DivisionCreate

from .course import create_random_course
from .professor import create_random_professor


def create_random_division(
    db: Session,
    course_id: Optional[int] = None,
    division_code: Optional[int] = None,
    professor_id: Optional[int] = None,
) -> Division:

    if course_id is None:
        course_id = create_random_course(db).id

    if professor_id is None:
        professor_id = create_random_professor(db).user_id

    return crud.division.create(
        db,
        obj_in=DivisionCreate(
            course_id=course_id, division_code=division_code or randint(1, 20), professor_id=professor_id
        ),
    )
