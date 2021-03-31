from typing import Any, Dict, Optional, Union

from sqlalchemy.orm import Session

from app.crud.base import CRUDBase
from app.models import Professor
from app.schemas import ProfessorCreate, ProfessorUpdate


class CRUDProfessor(CRUDBase[Professor, ProfessorCreate, ProfessorUpdate]):
    def get(self, db: Session, id: int) -> Optional[Professor]:
        return db.query(Professor).filter(Professor.user_id == id).first()

    def create(self, db: Session, *, obj_in: ProfessorCreate) -> Professor:
        db_obj = Professor(user_id=obj_in.user_id)
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def update(self, db: Session, *, db_obj: Professor, obj_in: Union[ProfessorUpdate, Dict[str, Any]]) -> Professor:
        if isinstance(obj_in, dict):
            update_data = obj_in
        else:
            update_data = obj_in.dict(exclude_unset=True)
        return super().update(db, db_obj=db_obj, obj_in=update_data)


professor = CRUDProfessor(Professor)
