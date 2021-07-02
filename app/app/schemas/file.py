from typing import Optional

from pydantic import BaseModel


class FileBase(BaseModel):
    owner_id: Optional[str]
    filename: Optional[str]
    course_id: Optional[str]


class FileCreate(FileBase):
    owner_id: str
    filename: str
    course_id: str


class FileUpdate(BaseModel):
    pass


class FileInDBBase(FileBase):
    id: Optional[str] = None

    class Config:
        orm_mode = True


# Additional properties to return via API
class File(FileInDBBase):
    pass


# Additional properties stored in DB
class FileInDB(FileInDBBase):
    pass
