from typing import Optional

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.crud.base import CRUDBase
from app.models import School
from app.schemas import SchoolCreate, SchoolUpdate


class CRUDSchool(CRUDBase[School, SchoolCreate, SchoolUpdate]):
    def get_by_name(self, db: Session, *, name: str) -> Optional[School]:
        return db.scalars(select(School).filter_by(name=name).limit(1)).first()

    def get_by_head(self, db: Session, *, head: str) -> Optional[School]:
        return db.scalars(select(School).filter_by(head=head).limit(1)).first()


school = CRUDSchool(School)
