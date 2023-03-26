from datetime import time
from typing import Optional, Sequence

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.crud.base import CRUDBase
from app.models import TimeSlot
from app.schemas import TimeSlotCreate, TimeSlotUpdate


class CRUDTimeSlot(CRUDBase[TimeSlot, TimeSlotCreate, TimeSlotUpdate]):
    def get_by_details(self, db: Session, *, start_time: time, end_time: time, school_id: str) -> Optional[TimeSlot]:
        return db.scalars(
            select(TimeSlot).filter_by(start_time=start_time, end_time=end_time, school_id=school_id).limit(1)
        ).first()

    def get_by_school(self, db: Session, *, school_id: str) -> Sequence[TimeSlot]:
        return db.scalars(select(TimeSlot).filter_by(school_id=school_id)).all()


timeslot = CRUDTimeSlot(TimeSlot)
