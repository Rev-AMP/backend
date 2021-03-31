from typing import Optional

from pydantic import BaseModel, validator

from .user import User


# Shared properties
class ProfessorBase(BaseModel):
    user_id: int

    @validator("user_id")
    def user_not_empty(cls, user_id: int) -> int:
        if user_id == 0:
            raise ValueError("Invalid user id!")
        return user_id


# Properties to receive via API on creation
class ProfessorCreate(ProfessorBase):
    user_id: int


# Properties to receive via API on update
class ProfessorUpdate(BaseModel):
    pass


# Properties to receive via API on remove
class ProfessorRemove(ProfessorBase):
    user_id: int


# Additional properties to return through API
class Professor(ProfessorBase):
    user: Optional[User]

    class Config:
        orm_mode = True