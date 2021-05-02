from datetime import time
from typing import Optional

from sqlalchemy.orm import Session

from app.crud.base import CRUDBase
from app.models import TimeSlot
from app.schemas import TimeSlotCreate, TimeSlotUpdate


class CRUDTimeSlot(CRUDBase[TimeSlot, TimeSlotCreate, TimeSlotUpdate]):
    def get_by_details(self, db: Session, *, start_time: time, end_time: time, school_id: str) -> Optional[TimeSlot]:
        return (
            db.query(TimeSlot)
            .filter(TimeSlot.start_time == start_time, TimeSlot.end_time == end_time, TimeSlot.school_id == school_id)
            .first()
        )


timeslot = CRUDTimeSlot(TimeSlot)
