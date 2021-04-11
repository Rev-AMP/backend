from typing import Optional

from sqlalchemy.orm import Session

from app.crud.base import CRUDBase
from app.models import Professor
from app.schemas import ProfessorCreate, ProfessorUpdate


class CRUDProfessor(CRUDBase[Professor, ProfessorCreate, ProfessorUpdate]):
    def get(self, db: Session, id: str) -> Optional[Professor]:
        return db.query(Professor).filter(Professor.user_id == id).first()

    def create(self, db: Session, *, obj_in: ProfessorCreate) -> Professor:
        db_obj = Professor(user_id=obj_in.user_id)
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj


professor = CRUDProfessor(Professor)
