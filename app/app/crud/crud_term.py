from datetime import date
from typing import Optional

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.crud.base import CRUDBase
from app.models import Term
from app.schemas import TermCreate, TermUpdate


class CRUDTerm(CRUDBase[Term, TermCreate, TermUpdate]):
    def get_by_details(
        self,
        db: Session,
        *,
        name: str,
        year_id: str,
        current_year_term: int,
        start_date: date,
        end_date: Optional[date],
    ) -> Optional[Term]:
        return db.scalars(
            select(Term)
            .filter_by(
                name=name,
                year_id=year_id,
                current_year_term=current_year_term,
                start_date=start_date,
                end_date=end_date,
            )
            .limit(1)
        ).first()


term = CRUDTerm(Term)
