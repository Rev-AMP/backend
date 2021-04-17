from typing import List, Optional

from sqlalchemy.orm import Session

from app.crud.base import CRUDBase
from app.models import Student, StudentDivision
from app.schemas.student_division import StudentDivisionCreate, StudentDivisionUpdate


class CRUDStudentDivision(CRUDBase[StudentDivision, StudentDivisionCreate, StudentDivisionUpdate]):
    @staticmethod
    def get_by_division(db: Session, division_id: str) -> Optional[List[StudentDivision]]:
        return db.query(StudentDivision).filter(StudentDivision.division_id == division_id).all()

    @staticmethod
    def get_by_student(db: Session, student_id: str) -> Optional[List[StudentDivision]]:
        return db.query(StudentDivision).filter(StudentDivision.student_id == student_id).all()

    @staticmethod
    def get_by_details(db: Session, division_id: str, student_id: str) -> Optional[StudentDivision]:
        return (
            db.query(StudentDivision)
            .filter(StudentDivision.student_id == student_id and StudentDivision.division_id == division_id)
            .first()
        )


student_division = CRUDStudentDivision(Student)
