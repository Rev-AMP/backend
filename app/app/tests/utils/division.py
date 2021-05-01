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
    course_id: Optional[str] = None,
    division_code: Optional[int] = None,
    professor_id: Optional[str] = None,
) -> Division:

    if course_id is None:
        course_id = create_random_course(db).id

    if professor_id is None:
        professor_id = create_random_professor(db).user_id

    if division_code is None:
        division_code = randint(1, 20)
        while crud.division.get_by_details(db=db, course_id=course_id, division_code=division_code):
            division_code = randint(1, 20)

    return crud.division.create(
        db,
        obj_in=DivisionCreate(course_id=course_id, division_code=division_code, professor_id=professor_id),
    )
