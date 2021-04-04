from typing import List, Optional

from sqlalchemy.orm import Session

from app.crud.base import CRUDBase
from app.models import Division
from app.schemas import DivisionCreate, DivisionUpdate


class CRUDDivision(CRUDBase[Division, DivisionCreate, DivisionUpdate]):
    def get_by_details(self, db: Session, *, course_id: int, division_code: int) -> Optional[Division]:
        return (
            db.query(Division)
            .filter(Division.course_id == course_id and Division.division_code == division_code)
            .first()
        )

    def get_all_divisions_for_professor(self, db: Session, professor_id: int) -> List[Division]:
        return db.query(Division).filter(Division.professor_id == professor_id).all()


division = CRUDDivision(Division)
