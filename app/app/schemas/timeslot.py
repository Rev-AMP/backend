from datetime import time
from typing import Dict, Optional

from pydantic import BaseModel, validator

from app.schemas.school import School


# shared properties
class TimeSlotBase(BaseModel):
    start_time: time
    end_time: time
    school_id: str

    @validator("start_time")
    def check_start_time(cls, start_time: time) -> time:
        return start_time

    @validator("end_time")
    def check_end_time(cls, end_time: time, values: Dict) -> Optional[time]:
        if values["start_time"] >= end_time:
            raise ValueError("A timeslot cannot end before it begins!")
        return end_time


# Properties to receive via API on creation
class TimeSlotCreate(TimeSlotBase):
    pass


# Properties to receive via API on update
class TimeSlotUpdate(BaseModel):
    start_time: Optional[time]
    end_time: Optional[time]

    @validator("start_time")
    def check_start_time(cls, start_time: Optional[time]) -> Optional[time]:
        return start_time

    @validator("end_time")
    def check_end_time(cls, end_time: Optional[time], values: Dict) -> Optional[time]:
        if start_time := values.get("start_time"):
            if end_time:
                if start_time > end_time:
                    raise ValueError("A timeslot cannot end before it begins!")
                return end_time
            raise ValueError("You need to pass one of start time or end time")
        if end_time:
            return end_time
        raise ValueError("You need to pass one of start time or end time")


class TimeSlotInDBBase(TimeSlotBase):
    id: Optional[str] = None

    class Config:
        orm_mode = True


# Additional properties to return via API
class TimeSlot(TimeSlotInDBBase):
    school: Optional[School]


# Additional properties stored in DB
class TimeSlotInDB(TimeSlotInDBBase):
    pass
