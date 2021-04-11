from typing import Optional

from pydantic import BaseModel

from .course import Course
from .users.professor import Professor


# shared properties
class DivisionBase(BaseModel):
    course_id: Optional[str] = None
    division_code: Optional[int] = None
    professor_id: Optional[str] = None


# Properties to receive via API on creation
class DivisionCreate(DivisionBase):
    course_id: str
    division_code: int
    professor_id: str


# Properties to receive via API on update
class DivisionUpdate(DivisionBase):
    pass


# Additional properties to return through API
class Division(DivisionBase):
    id: Optional[str] = None
    course: Optional[Course]
    professor: Optional[Professor]

    class Config:
        orm_mode = True
