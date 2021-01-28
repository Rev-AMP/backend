from typing import Optional

from pydantic import BaseModel


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
