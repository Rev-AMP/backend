from typing import List, Optional

from sqlalchemy.orm import Session

from app.crud.base import CRUDBase
from app.models import Course
from app.schemas import CourseCreate, CourseUpdate


class CRUDCourse(CRUDBase[Course, CourseCreate, CourseUpdate]):
    def get_by_details(self, db: Session, *, name: str, code: str, term_id: int) -> Optional[Course]:
        return (
            db.query(Course).filter(Course.name == name and Course.code == code and Course.term_id == term_id).first()
        )

    def get_by_name(self, db: Session, *, name: str) -> Optional[Course]:
        return db.query(Course).filter(Course.name == name).first()

    def get_by_code(self, db: Session, *, code: str) -> List[Course]:
        return db.query(Course).filter(Course.code == code).all()

    def get_by_term(self, db: Session, *, term_id: int) -> List[Course]:
        return db.query(Course).filter(Course.term_id == term_id).all()


course = CRUDCourse(Course)
