from typing import Optional

from pydantic import BaseModel

from app.models.users.user import User


# Shared properties
class AdminBase(BaseModel):
    user: Optional[User] = None
    permissions: Optional[int] = 0


# Properties to receive via API on creation
class AdminCreate(AdminBase):
    user: User
    permissions: int


# Properties to receive via API on update
class AdminUpdate(AdminBase):
    permissions: Optional[int]
