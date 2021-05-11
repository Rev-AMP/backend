import calendar
import random

from sqlalchemy.orm import Session

from app import crud
from app.schemas import LectureUpdate
from app.tests.utils.lecture import create_random_lecture

from ..utils.division import create_random_division
from ..utils.timeslot import create_random_timeslot


def test_create_lecture(db: Session) -> None:
    day = random.choice(calendar.day_name)
    time_slot_id = create_random_timeslot(db).id
    division_id = create_random_division(db).id
    type_ = random.choice(["theory", "practical", "tutorial"])
    room_number = random.choice(["A", "B", "C"]) + "".join(map(str, (random.sample(range(5), 3))))
    lecture = create_random_lecture(
        db, day=day, time_slot_id=time_slot_id, division_id=division_id, type_=type_, room_number=room_number
    )
    assert lecture
    assert lecture.time_slot_id == time_slot_id
    assert lecture.division_id == division_id
    assert lecture.type == type_
    assert lecture.room_number == room_number


def test_update_lecture(db: Session) -> None:
    lecture = create_random_lecture(db)
    assert lecture
    type_ = random.choice(["theory", "practical", "tutorial"])
    updated_lecture = crud.lecture.update(db, db_obj=lecture, obj_in=LectureUpdate(type=type_))
    assert updated_lecture.type == type_


def test_lecture_by_details(db: Session) -> None:
    lecture = create_random_lecture(db)
    assert lecture.id
    assert lecture.time_slot_id
    assert lecture.division_id
    assert lecture.type
    assert lecture.room_number
    fetched_lecture = crud.lecture.get_by_details(
        db,
        day=lecture.day,
        time_slot_id=lecture.time_slot_id,
        division_id=lecture.division_id,
        type=lecture.type,
        room_number=lecture.room_number,
    )
    assert fetched_lecture
    assert fetched_lecture.id == lecture.id
