from typing import Optional

from sqlalchemy.orm import Session

from app.crud.base import CRUDBase
from app.models import Division
from app.schemas import DivisionCreate, DivisionUpdate


class CRUDDivision(CRUDBase[Division, DivisionCreate, DivisionUpdate]):
    def get_by_details(self, db: Session, *, course_id: str, division_code: int) -> Optional[Division]:
        return (
            db.query(Division).filter(Division.course_id == course_id, Division.division_code == division_code).first()
        )


division = CRUDDivision(Division)
