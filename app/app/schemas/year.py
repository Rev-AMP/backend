from datetime import datetime
from typing import Optional

from pydantic import BaseModel, validator


# Shared properties
class YearBase(BaseModel):
    school_id: Optional[int] = None
    start_year: Optional[int] = None
    end_year: Optional[int] = None
    is_active: Optional[bool] = True


# Properties to receive via API on creation
class YearCreate(YearBase):
    school_id: int
    start_year: int
    end_year: int

    @validator('start_year')
    def validate_start_year(cls, start_year: int) -> int:
        current_year = datetime.now().year
        if start_year > current_year + 1:
            raise ValueError("You can't work so much in the future!")
        if start_year < current_year:
            raise ValueError("You can't work so much in the past!")
        return current_year

    @validator('end_year')
    def validate_end_year(cls, end_year: int, values: dict) -> int:
        if end_year < values['start_year']:
            raise ValueError("You can't end the year before it starts")
        return end_year


# Properties to receive via API on update
class YearUpdate(YearBase):
    pass


class YearInDBBase(YearBase):
    id: Optional[int] = None

    class Config:
        orm_mode = True


# Additional properties to return via API
class Year(YearInDBBase):
    pass


# Additional properties stored in DB
class YearInDB(YearInDBBase):
    pass
