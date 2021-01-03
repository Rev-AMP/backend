from typing import Optional

from pydantic import BaseModel


# Shared properties
class AdminBase(BaseModel):
    user_id: Optional[int] = None
    permissions: Optional[int] = 0


# Properties to receive via API on creation
class AdminCreate(AdminBase):
    user_id: int
    permissions: int


# Properties to receive via API on update
class AdminUpdate(AdminBase):
    permissions: Optional[int]
