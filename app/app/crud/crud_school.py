from typing import List, Optional

from sqlalchemy.orm import Session

from app.crud.base import CRUDBase
from app.models import School, User
from app.schemas import SchoolCreate, SchoolUpdate


class CRUDSchool(CRUDBase[School, SchoolCreate, SchoolUpdate]):
    def get_by_name(self, db: Session, *, name: str) -> Optional[School]:
        return db.query(School).filter(School.name == name).first()

    def get_by_head(self, db: Session, *, head: str) -> Optional[School]:
        return db.query(School).filter(School.head == head).first()

    def get_all_students(self, db: Session, *, school_id: int) -> List[User]:
        return db.query(User).filter(User.type == "student").filter(User.school_id == school_id).all()

    def get_all_professors(self, db: Session, *, school_id: int) -> List[User]:
        return db.query(User).filter(User.type == "professor").filter(User.school_id == school_id).all()


school = CRUDSchool(School)
