from datetime import date
from typing import Optional

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
        return (
            db.query(Term)
            .filter(
                Term.name == name,
                Term.year_id == year_id,
                Term.current_year_term == current_year_term,
                Term.start_date == start_date,
                Term.end_date == end_date,
            )
            .first()
        )


term = CRUDTerm(Term)
