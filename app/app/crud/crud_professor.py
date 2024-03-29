import logging
from typing import Optional

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.crud.base import CRUDBase
from app.models import Professor
from app.schemas import ProfessorCreate, ProfessorUpdate


class CRUDProfessor(CRUDBase[Professor, ProfessorCreate, ProfessorUpdate]):
    def get(self, db: Session, id: str) -> Optional[Professor]:
        return db.scalars(select(Professor).filter_by(user_id=id).limit(1)).first()

    def create(self, db: Session, *, obj_in: ProfessorCreate) -> Professor:
        db_obj = Professor(user_id=obj_in.user_id)
        db.add(db_obj)
        try:
            db.commit()
        except Exception as e:
            logging.error(f"{e.__class__} - {e.__str__}")
            db.rollback()
        db.refresh(db_obj)
        return db_obj


professor = CRUDProfessor(Professor)
