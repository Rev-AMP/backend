from typing import Optional

from pydantic import BaseModel

from app.schemas import Term


# shared properties
class CourseBase(BaseModel):
    name: Optional[str] = None
    code: Optional[str] = None
    term_id: Optional[int] = None


# Properties to receive via API on creation
class CourseCreate(CourseBase):
    name: str
    code: str
    term_id: int


# Properties to receive via API on update
class CourseUpdate(CourseBase):
    pass


class CourseInDBBase(CourseBase):
    id: Optional[int] = None

    class Config:
        orm_mode = True


# Additional properties to return via API
class Course(CourseInDBBase):
    term: Optional[Term]


# Additional properties stored in DB
class CourseInDB(CourseInDBBase):
    pass
