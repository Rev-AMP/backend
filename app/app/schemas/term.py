from typing import Optional

from pydantic import BaseModel
from sqlalchemy.types import Date


# Shared properties
class TermBase(BaseModel):
    name: Optional[str] = None
    year_id: Optional[int] = None
    current_year_term: Optional[int] = None
    start_date: Optional[Date] = None
    end_date: Optional[Date] = None
    has_electives: Optional[bool] = False
    is_active: Optional[bool] = True


# Properties to receive via API on creation
class TermCreate(TermBase):
    name: str
    year_id: int
    start_date: Date
    current_year_term: int
    has_electives: bool


# Properties to receive via API on update
class TermUpdate(TermBase):
    pass


class TermInDBBase(TermBase):
    id: Optional[int] = None

    class Config:
        orm_mode = True


# Additional properties to return via API
class Term(TermInDBBase):
    pass


# Additional properties stored in DB
class TermInDB(TermInDBBase):
    pass
