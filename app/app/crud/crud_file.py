from typing import List

from sqlalchemy.orm import Session

from app.crud.base import CRUDBase
from app.models import File
from app.schemas import FileCreate, FileUpdate


class CRUDFile(CRUDBase[File, FileCreate, FileUpdate]):
    def get_by_owner_course(self, db: Session, *, course_id: str, owner_id: str) -> List[File]:
        return db.query(File).filter(File.course_id == course_id, File.owner_id == owner_id).all()

    def get_by_owner(self, db: Session, *, owner_id: str) -> List[File]:
        return db.query(File).filter(File.owner_id == owner_id).all()

    def get_by_course(self, db: Session, *, course_id: str) -> List[File]:
        return db.query(File).filter(File.course_id == course_id).all()


file = CRUDFile(File)
