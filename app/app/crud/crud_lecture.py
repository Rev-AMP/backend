from typing import Optional, Sequence

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.crud.base import CRUDBase
from app.models import Lecture
from app.schemas import LectureCreate, LectureUpdate


class CRUDLecture(CRUDBase[Lecture, LectureCreate, LectureUpdate]):
    def get_by_details(
        self, db: Session, *, day: str, time_slot_id: str, division_id: str, type: str, room_number: str
    ) -> Optional[Lecture]:
        return db.scalars(
            select(Lecture)
            .filter_by(
                day=day,
                time_slot_id=time_slot_id,
                division_id=division_id,
                type=type,
                room_number=room_number,
            )
            .limit(1)
        ).first()

    def get_by_division(self, db: Session, *, division_id: str) -> Sequence[Lecture]:
        return db.scalars(select(Lecture).filter_by(division_id=division_id)).all()

    def get_by_day_division(self, db: Session, *, day: str, division_id: str) -> Sequence[Lecture]:
        return db.scalars(select(Lecture).filter_by(day=day, division_id=division_id)).all()


lecture = CRUDLecture(Lecture)
