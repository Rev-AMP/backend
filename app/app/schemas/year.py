from datetime import datetime
from typing import Optional

from pydantic import BaseModel, validator

from app.schemas.school import School


# Shared properties
class YearBase(BaseModel):
    name: Optional[str] = None
    school_id: Optional[str] = None
    start_year: Optional[int] = None
    end_year: Optional[int] = None
    is_active: Optional[bool] = True

    @validator("name")
    def name_not_empty(cls, name: Optional[str]) -> Optional[str]:
        if name is not None and name == "":
            raise ValueError("Name must not be empty!")
        return name

    @validator("start_year")
    def validate_start_year(cls, start_year: Optional[int]) -> Optional[int]:
        if start_year:
            current_year = datetime.now().year
            if start_year > current_year + 1:
                raise ValueError("You can't work so much in the future!")
            if start_year < current_year - 1:
                raise ValueError("You can't work so much in the past!")
        return start_year

    @validator("end_year")
    def validate_end_year(cls, end_year: Optional[int], values: dict) -> Optional[int]:
        if end_year:
            if values.get("start_year"):
                if end_year < values["start_year"]:
                    raise ValueError("You can't end the year before it starts")
            if end_year < datetime.now().year - 1:
                raise ValueError("You can't work so much in the past!")
        return end_year


# Properties to receive via API on creation
class YearCreate(YearBase):
    name: str
    school_id: str
    start_year: int
    end_year: int


# Properties to receive via API on update
class YearUpdate(YearBase):
    pass


class YearInDBBase(YearBase):
    id: Optional[str] = None

    class Config:
        orm_mode = True


# Additional properties to return via API
class Year(YearInDBBase):
    school: Optional[School]


# Additional properties stored in DB
class YearInDB(YearInDBBase):
    pass
