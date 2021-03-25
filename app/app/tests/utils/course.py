from random import randint
from typing import Optional

from sqlalchemy.orm import Session

from app import crud
from app.models import Course
from app.schemas import CourseCreate

from .term import create_random_term
from .utils import random_lower_string


def create_random_course(
    db: Session,
    name: Optional[str] = None,
    course_code: Optional[str] = None,
    panel_code: Optional[int] = None,
    elective_code: Optional[str] = None,
    term_id: Optional[int] = None,
) -> Course:

    if term_id is None:
        term_id = create_random_term(db).id

    return crud.course.create(
        db=db,
        obj_in=CourseCreate(
            name=name or random_lower_string(),
            course_code=course_code or random_lower_string()[:20],  # To ensure course code under 20 characters
            panel_code=panel_code or randint(1, 11),
            elective_code=elective_code or random_lower_string()[:20],
            term_id=term_id,
        ),
    )
