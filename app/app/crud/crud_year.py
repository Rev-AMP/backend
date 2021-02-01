from typing import List

from sqlalchemy.orm import Session

from app.crud.base import CRUDBase
from app.models import Year
from app.schemas import YearCreate, YearUpdate


class CRUDYear(CRUDBase[Year, YearCreate, YearUpdate]):
    def get_by_school(self, db: Session, *, school_id: int) -> List[Year]:
        return db.query(Year).filter(Year.school_id == school_id).all()

    def get_by_start(self, db: Session, *, start_year: int) -> List[Year]:
        return db.query(Year).filter(Year.start_year == start_year).all()

    def get_by_end(self, db: Session, *, end_year: int) -> List[Year]:
        return db.query(Year).filter(Year.end_year == end_year).all()


year = CRUDYear(Year)
