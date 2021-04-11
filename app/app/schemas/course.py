from typing import Optional

from pydantic import BaseModel, validator

from app.schemas.term import Term


# shared properties
class CourseBase(BaseModel):
    name: Optional[str] = None
    course_code: Optional[str] = None
    elective_code: Optional[str] = None
    term_id: Optional[str] = None

    @validator("name")
    def name_not_empty(cls, name: Optional[str]) -> Optional[str]:
        if name is not None and name == "":
            raise ValueError("Course name must not be empty!")
        return name

    @validator("course_code")
    def code_not_empty(cls, course_code: Optional[str]) -> Optional[str]:
        if course_code is not None and course_code == "":
            raise ValueError("Course code must not be empty!")
        return course_code


# Properties to receive via API on creation
class CourseCreate(CourseBase):
    name: str
    course_code: str
    term_id: str


# Properties to receive via API on update
class CourseUpdate(CourseBase):
    pass


class CourseInDBBase(CourseBase):
    id: Optional[str] = None

    class Config:
        orm_mode = True


# Additional properties to return via API
class Course(CourseInDBBase):
    term: Optional[Term]


# Additional properties stored in DB
class CourseInDB(CourseInDBBase):
    pass
