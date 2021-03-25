from typing import Optional

from sqlalchemy.orm import Session

from app.crud.base import CRUDBase
from app.models import Course
from app.schemas import CourseCreate, CourseUpdate


class CRUDCourse(CRUDBase[Course, CourseCreate, CourseUpdate]):
    def get_by_details(
        self, db: Session, *, name: str, course_code: str, panel_code: int, term_id: int
    ) -> Optional[Course]:
        return (
            db.query(Course)
            .filter(
                Course.name == name
                and Course.course_code == course_code
                and Course.panel_code == panel_code
                and Course.term_id == term_id
            )
            .first()
        )


course = CRUDCourse(Course)
