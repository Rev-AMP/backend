from typing import Optional

from pydantic import BaseModel, validator

from ..term import Term
from .user import User


# Shared properties
class StudentBase(BaseModel):
    user_id: Optional[int] = None
    term_id: Optional[int]

    @validator('user_id')
    def user_not_empty(cls, user_id: Optional[int]) -> Optional[int]:
        if user_id is None:
            raise ValueError("User ID must not be empty!")
        if user_id == 0:
            raise ValueError("Invalid user id!")
        return user_id


# Properties to receive via API on creation
class StudentCreate(StudentBase):
    user_id: int


# Properties to receive via API on update
class StudentUpdate(BaseModel):
    term_id: int

    @validator('term_id')
    def user_not_empty(cls, term_id: int) -> int:
        if term_id < 1:
            raise ValueError("Invalid term id!")
        return term_id


# Properties to receive via API on remove
class StudentRemove(StudentBase):
    user_id: int


# Additional properties to return through API
class Student(StudentBase):
    user: Optional[User]
    term: Optional[Term]

    class Config:
        orm_mode = True
