from typing import Optional

from sqlalchemy.orm import Session

from app.crud.base import CRUDBase
from app.models import Year
from app.schemas import YearCreate, YearUpdate


class CRUDYear(CRUDBase[Year, YearCreate, YearUpdate]):
    def get_by_details(
        self, db: Session, *, name: str, school_id: str, start_year: int, end_year: int
    ) -> Optional[Year]:
        return (
            db.query(Year)
            .filter(
                Year.name == name, Year.school_id == school_id, Year.start_year == start_year, Year.end_year == end_year
            )
            .first()
        )


year = CRUDYear(Year)
