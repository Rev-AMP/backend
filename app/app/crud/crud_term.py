from typing import List, Optional
from sqlalchemy.types import Date

from sqlalchemy.orm import Session

from app.crud.base import CRUDBase
from app.models import Term
from app.schemas import TermCreate, TermUpdate


class CRUDTerm(CRUDBase[Term, TermCreate, TermUpdate]):
    def get_by_name(self, db: Session, *, name: str) -> Optional[Term]:
        return db.query(Term).filter(Term.name == name)

    def get_by_year(self, db: Session, *, year_id: int) -> List[Term]:
        return db.query(Term).filter(Term.year_id == year_id).all()

    def get_by_start(self, db: Session, *, start_date: Date) -> List[Term]:
        return db.query(Term).filter(Term.start_date == start_date).all()

    def get_by_end(self, db: Session, *, end_date: Date) -> List[Term]:
        return db.query(Term).filter(Term.end_date == end_date).all()


term = CRUDTerm(Term)
