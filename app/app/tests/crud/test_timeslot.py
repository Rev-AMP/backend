from datetime import datetime, timedelta

from sqlalchemy.orm import Session

from app import crud
from app.schemas import TimeSlotUpdate
from app.tests.utils.timeslot import create_random_timeslot

from ..utils.school import create_random_school


def test_create_timeslot(db: Session) -> None:
    start_time = datetime.now().time()
    end_time = (datetime.now() + timedelta(hours=1)).time()
    school_id = create_random_school(db).id
    timeslot = create_random_timeslot(db, start_time=start_time, end_time=end_time, school_id=school_id)
    assert timeslot
    assert timeslot.start_time == start_time
    assert timeslot.end_time == end_time


def test_update_timeslot(db: Session) -> None:
    timeslot = create_random_timeslot(db)
    assert timeslot
    end_time = (datetime.now() + timedelta(minutes=30)).time()
    updated_timeslot = crud.timeslot.update(db, db_obj=timeslot, obj_in=TimeSlotUpdate(end_time=end_time))
    assert updated_timeslot.end_time == end_time


def test_timeslot_by_details(db: Session) -> None:
    timeslot = create_random_timeslot(db)
    assert timeslot.id
    assert timeslot.start_time
    assert timeslot.end_time
    assert timeslot.school_id
    fetched_timeslot = crud.timeslot.get_by_details(
        db,
        start_time=timeslot.start_time,
        end_time=timeslot.end_time,
        school_id=timeslot.school_id,
    )
    assert fetched_timeslot
    assert fetched_timeslot.id == timeslot.id


def test_timeslot_by_school(db: Session) -> None:
    timeslot = create_random_timeslot(db)
    assert timeslot.id
    assert timeslot.school_id
    fetched_timeslot = crud.timeslot.get_by_school(db, school_id=timeslot.school_id)[0]
    assert fetched_timeslot
    assert fetched_timeslot.id == timeslot.id
