from typing import Optional

from pydantic import BaseModel, validator

from ..term import Term
from .user import User


# Shared properties
class StudentBase(BaseModel):
    user_id: str
    term_id: Optional[str] = None

    @validator("user_id")
    def user_not_empty(cls, user_id: str) -> str:
        if user_id == "":
            raise ValueError("Invalid user id!")
        return user_id


# Properties to receive via API on creation
class StudentCreate(StudentBase):
    user_id: str


# Properties to receive via API on update
class StudentUpdate(BaseModel):
    term_id: str

    @validator("term_id")
    def user_not_empty(cls, term_id: str) -> str:
        if term_id == "":
            raise ValueError("Invalid term id!")
        return term_id


# Properties to receive via API on remove
class StudentRemove(StudentBase):
    user_id: str


# Additional properties to return through API
class Student(StudentBase):
    user: Optional[User]
    term: Optional[Term]

    class Config:
        orm_mode = True
