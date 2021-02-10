from typing import Optional

from pydantic import BaseModel


# Shared properties
class TermBase(BaseModel):
    year_id: Optional[int] = None
    start_date: Optional[str] = None
    end_date: Optional[str] = None
    current_Term_term: Optional[int] = None
    term_number: Optional[int] = None
    has_electives: Optional[bool] = False
    is_active: Optional[bool] = True


# Properties to receive via API on creation
class TermCreate(TermBase):
    Term_id: int
    start_date: str
    current_Term_term: int
    term_number: int
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
