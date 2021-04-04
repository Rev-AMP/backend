from typing import Optional

from sqlalchemy.orm import Session

from app.crud.base import CRUDBase
from app.models import School
from app.schemas import SchoolCreate, SchoolUpdate


class CRUDSchool(CRUDBase[School, SchoolCreate, SchoolUpdate]):
    def get_by_name(self, db: Session, *, name: str) -> Optional[School]:
        return db.query(School).filter(School.name == name).first()

    def get_by_head(self, db: Session, *, head: str) -> Optional[School]:
        return db.query(School).filter(School.head == head).first()


school = CRUDSchool(School)
