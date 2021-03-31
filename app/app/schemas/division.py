from typing import Optional

from pydantic import BaseModel

from .users.professor import Professor
from .course import Course


# shared properties
class DivisionBase(BaseModel):
    course_id: Optional[int] = None
    division_code: Optional[int] = None
    professor_id: Optional[int] = None


# Properties to receive via API on creation
class DivisionCreate(DivisionBase):
    course_id: int
    division_code: int
    professor_id: int


# Properties to receive via API on update
class DivisionUpdate(BaseModel):
    pass


# Additional properties to return through API
class Division(DivisionBase):
    course: Optional[Course]
    professor: Optional[Professor]

    class Config:
        orm_mode = True
