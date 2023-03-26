from typing import Optional

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.crud.base import CRUDBase
from app.models import Division
from app.schemas import DivisionCreate, DivisionUpdate


class CRUDDivision(CRUDBase[Division, DivisionCreate, DivisionUpdate]):
    def get_by_details(self, db: Session, *, course_id: str, division_code: int) -> Optional[Division]:
        return db.scalars(select(Division).filter_by(course_id=course_id, division_code=division_code).limit(1)).first()


division = CRUDDivision(Division)
