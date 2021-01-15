from typing import List, Optional

from sqlalchemy.orm import Session

from app.crud.base import CRUDBase
from app.models import User
from app.models.school import School
from app.schemas.school import SchoolCreate, SchoolUpdate


class CRUDSchool(CRUDBase[School, SchoolCreate, SchoolUpdate]):
    def get_by_name(self, db: Session, *, name: str) -> Optional[School]:
        return db.query(School).filter(School.name == name).first()

    def get_all_students(self, db: Session, *, school_id: int) -> List[User]:
        return db.query(User).filter(User.type == "student").filter(User.school == school_id)

    def get_all_professors(self, db: Session, *, school_id: int) -> List[User]:
        return db.query(User).filter(User.type == "professor").filter(User.school == school_id)


school = CRUDSchool(School)
