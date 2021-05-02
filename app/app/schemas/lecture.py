import calendar
from typing import Optional

from pydantic import BaseModel, validator

from app.schemas.division import Division
from app.schemas.timeslot import TimeSlot


# shared properties
class LectureBase(BaseModel):
    day: Optional[str]
    time_slot_id: Optional[str]
    division_id: Optional[str]
    type: Optional[str]
    room_number: Optional[str]

    @validator("day")
    def valid_day(cls, day: Optional[str]) -> Optional[str]:
        if day:
            if day == "":
                raise ValueError("Day must not be empty!")
            if day not in [x for x in calendar.day_name]:
                raise ValueError(f"Invalid day {day}")
        return day

    @validator("type")
    def valid_type(cls, type: Optional[str]) -> Optional[str]:
        if type:
            if type == "":
                raise ValueError("Lecture type must not be empty!")
            if type not in ("theory", "practical", "tutorial"):
                raise ValueError(f"Invalid lecture type {type}")
        return type


# Properties to receive via API on creation
class LectureCreate(LectureBase):
    day: str
    time_slot_id: str
    division_id: str
    type: str
    room_number: str


# Properties to receive via API on update
class LectureUpdate(LectureBase):
    pass


class LectureInDBBase(LectureBase):
    id: Optional[str] = None

    class Config:
        orm_mode = True


# Additional properties to return via API
class Lecture(LectureInDBBase):
    division: Optional[Division]
    time_slot: Optional[TimeSlot]


# Additional properties stored in DB
class LectureInDB(LectureInDBBase):
    pass
