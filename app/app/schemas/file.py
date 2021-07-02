from typing import Optional

from pydantic import BaseModel
from sqlalchemy.sql.expression import desc

from app.schemas.course import Course
from app.schemas.users.user import User


class FileBase(BaseModel):
    owner_id: Optional[str]
    filename: Optional[str]
    course_id: Optional[str]
    file_type: Optional[str]
    submission_id: Optional[str]
    marks: Optional[int]
    description: Optional[str]


class FileCreate(FileBase):
    owner_id: str
    filename: str
    course_id: str
    file_type: str
    description: str


class FileUpdate(BaseModel):
    marks: int


class FileInDBBase(FileBase):
    id: Optional[str] = None

    class Config:
        orm_mode = True


# Additional properties to return via API
class File(FileInDBBase):
    owner: Optional[User]
    course: Optional[Course]


# Additional properties stored in DB
class FileInDB(FileInDBBase):
    pass
