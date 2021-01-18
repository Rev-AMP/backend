from typing import Optional

from pydantic import BaseModel


# Shared properties
class SchoolBase(BaseModel):
    name: Optional[str] = None
    head: Optional[str] = None


# Properties to receive via API on creation
class SchoolCreate(SchoolBase):
    name: str


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
