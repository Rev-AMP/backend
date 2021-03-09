from datetime import date
from typing import List, Optional

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
        year_id: int,
        current_year_term: int,
        start_date: date,
        end_date: Optional[date]
    ) -> Optional[Term]:
        return (
            db.query(Term)
            .filter(
                Term.name == name
                and Term.year_id == year_id
                and Term.current_year_term == current_year_term
                and Term.start_date == start_date
                and Term.end_date == end_date
            )
            .first()
        )

    def get_by_year_term(self, db: Session, *, year_id: int, current_year_term: int) -> Optional[Term]:
        return db.query(Term).filter(Term.year_id == year_id and Term.current_year_term == current_year_term).first()

    def get_by_name(self, db: Session, *, name: str) -> List[Term]:
        return db.query(Term).filter(Term.name == name).all()

    def get_by_year(self, db: Session, *, year_id: int) -> List[Term]:
        return db.query(Term).filter(Term.year_id == year_id).all()

    def get_by_start(self, db: Session, *, start_date: date) -> List[Term]:
        return db.query(Term).filter(Term.start_date == start_date).all()

    def get_by_end(self, db: Session, *, end_date: date) -> List[Term]:
        return db.query(Term).filter(Term.end_date == end_date).all()


term = CRUDTerm(Term)
