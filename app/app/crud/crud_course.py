from typing import Optional

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.crud.base import CRUDBase
from app.models import Course
from app.schemas import CourseCreate, CourseUpdate


class CRUDCourse(CRUDBase[Course, CourseCreate, CourseUpdate]):
    def get_by_details(self, db: Session, *, name: str, course_code: str, term_id: str) -> Optional[Course]:
        return db.scalars(
            select(Course).filter_by(name=name, course_code=course_code, term_id=term_id).limit(1)
        ).first()


course = CRUDCourse(Course)
