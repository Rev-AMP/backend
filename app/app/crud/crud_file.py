from typing import Sequence

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.crud.base import CRUDBase
from app.models import File
from app.schemas import FileCreate, FileUpdate


class CRUDFile(CRUDBase[File, FileCreate, FileUpdate]):
    def get_by_owner_course(self, db: Session, *, course_id: str, owner_id: str) -> Sequence[File]:
        return db.scalars(select(File).filter_by(course_id=course_id, owner_id=owner_id)).all()

    def get_by_owner(self, db: Session, *, owner_id: str) -> Sequence[File]:
        return db.scalars(select(File).filter_by(owner_id=owner_id)).all()

    def get_by_course(self, db: Session, *, course_id: str) -> Sequence[File]:
        return db.scalars(select(File).filter_by(course_id=course_id)).all()

    def get_by_submission(self, db: Session, *, submission_id: str) -> Sequence[File]:
        return db.scalars(select(File).filter_by(submission_id=submission_id)).all()


file = CRUDFile(File)
