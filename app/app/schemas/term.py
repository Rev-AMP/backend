from datetime import date
from typing import Optional

from pydantic import BaseModel

from app.schemas.year import Year


# Shared properties
class TermBase(BaseModel):
    name: Optional[str] = None
    year_id: Optional[str] = None
    current_year_term: Optional[int] = None
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    has_electives: Optional[bool] = False
    is_active: Optional[bool] = True


# Properties to receive via API on creation
class TermCreate(TermBase):
    name: str
    year_id: str
    start_date: date
    current_year_term: int
    has_electives: bool


# Properties to receive via API on update
class TermUpdate(TermBase):
    pass


class TermInDBBase(TermBase):
    id: Optional[str] = None

    class Config:
        orm_mode = True


# Additional properties to return via API
class Term(TermInDBBase):
    year: Optional[Year]


# Additional properties stored in DB
class TermInDB(TermInDBBase):
    pass
