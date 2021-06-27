from datetime import datetime, time
from typing import Optional

from sqlalchemy.orm import Session

from app import crud
from app.models import TimeSlot
from app.schemas import TimeSlotCreate

from .school import create_random_school


def create_random_timeslot(
    db: Session,
    start_time: Optional[time] = None,
    end_time: Optional[time] = None,
    school_id: Optional[str] = None,
) -> TimeSlot:

    if start_time is None:
        start_time = datetime.now().time()

    if end_time is None:
        end_time = datetime.now().time()

    if school_id is None:
        school_id = create_random_school(db).id

    return crud.timeslot.create(
        db=db, obj_in=TimeSlotCreate(db=db, start_time=start_time, end_time=end_time, school_id=school_id)
    )
