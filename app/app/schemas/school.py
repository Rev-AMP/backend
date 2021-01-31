from typing import Optional

from pydantic import BaseModel, validator


# Shared properties
class SchoolBase(BaseModel):
    name: Optional[str] = None
    head: Optional[str] = None


# Properties to receive via API on creation
class SchoolCreate(SchoolBase):
    name: str
    head: str

    @validator('name')
    def name_not_empty(cls, name: str) -> None:
        if not name:
            raise ValueError("Name must not be empty!")

    @validator('head')
    def head_not_empty(cls, head: str) -> None:
        if not head:
            raise ValueError("Head name must not be empty!")


# Properties to receive via API on update
class SchoolUpdate(SchoolBase):
    pass


class SchoolInDBBase(SchoolBase):
    id: Optional[int] = None

    class Config:
        orm_mode = True


# Additional properties to return via API
class School(SchoolInDBBase):
    pass


# Additional properties stored in DB
class SchoolInDB(SchoolInDBBase):
    pass
