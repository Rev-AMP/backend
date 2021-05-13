from typing import List, Optional

from sqlalchemy.orm import Session

from app.crud.base import CRUDBase
from app.models import Lecture
from app.schemas import LectureCreate, LectureUpdate


class CRUDLecture(CRUDBase[Lecture, LectureCreate, LectureUpdate]):
    def get_by_details(
        self, db: Session, *, day: str, time_slot_id: str, division_id: str, type: str, room_number: str
    ) -> Optional[Lecture]:
        return (
            db.query(Lecture)
            .filter(
                Lecture.day == day,
                Lecture.time_slot_id == time_slot_id,
                Lecture.division_id == division_id,
                Lecture.type == type,
                Lecture.room_number == room_number,
            )
            .first()
        )

    def get_by_division(self, db: Session, *, division_id: str) -> List[Lecture]:
        return db.query(Lecture).filter(Lecture.division_id == division_id).all()


lecture = CRUDLecture(Lecture)