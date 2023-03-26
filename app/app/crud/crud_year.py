from typing import Optional

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.crud.base import CRUDBase
from app.models import Year
from app.schemas import YearCreate, YearUpdate


class CRUDYear(CRUDBase[Year, YearCreate, YearUpdate]):
    def get_by_details(
        self, db: Session, *, name: str, school_id: str, start_year: int, end_year: int
    ) -> Optional[Year]:
        return db.scalars(
            select(Year).filter_by(name=name, school_id=school_id, start_year=start_year, end_year=end_year).limit(1)
        ).first()


year = CRUDYear(Year)
