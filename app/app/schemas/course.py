from typing import Optional

from pydantic import BaseModel, validator

from app.schemas import Term


# shared properties
class CourseBase(BaseModel):
    name: Optional[str] = None
    code: Optional[str] = None
    term_id: Optional[int] = None

    @validator('name')
    def name_not_empty(cls, name: Optional[str]) -> Optional[str]:
        if name is not None and name == "":
            raise ValueError("Course name must not be empty!")
        return name

    @validator('code')
    def code_not_empty(cls, code: Optional[str]) -> Optional[str]:
        if code is not None and code == "":
            raise ValueError("Course code must not be empty!")
        return code


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
