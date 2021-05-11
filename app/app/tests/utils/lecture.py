import calendar
import random
from typing import Optional

from sqlalchemy.orm import Session

from app import crud
from app.models import Lecture
from app.schemas import LectureCreate

from .division import create_random_division
from .timeslot import create_random_timeslot


def create_random_lecture(
    db: Session,
    day: Optional[str] = None,
    time_slot_id: Optional[str] = None,
    division_id: Optional[str] = None,
    type_: Optional[str] = None,
    room_number: Optional[str] = None,
) -> Lecture:

    if day is None:
        day = random.choice(calendar.day_name)

    if time_slot_id is None:
        time_slot_id = create_random_timeslot(db).id

    if division_id is None:
        division_id = create_random_division(db).id

    if type_ is None:
        type_ = random.choice(["theory", "practical", "tutorial"])

    if room_number is None:
        room_number = random.choice(["A", "B", "C"]) + "".join(map(str, (random.sample(range(5), 3))))
        while crud.lecture.get_by_details(
            db=db, day=day, time_slot_id=time_slot_id, division_id=division_id, type=type_, room_number=room_number
        ):
            room_number = random.choice(["A", "B", "C"]) + "".join(map(str, (random.sample(range(5), 3))))

    return crud.lecture.create(
        db=db,
        obj_in=LectureCreate(
            db=db, day=day, time_slot_id=time_slot_id, division_id=division_id, type=type_, room_number=room_number
        ),
    )
