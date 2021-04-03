from typing import Optional

from pydantic import BaseModel

from .course import Course
from .users.professor import Professor


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
    id: int
    course: Optional[Course]
    professor: Optional[Professor]

    class Config:
        orm_mode = True
