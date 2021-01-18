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
    user_id: int
    permissions: int


# Properties to receive via API on remove
class AdminRemove(AdminBase):
    user_id: int


# Additional properties to return through API
class Admin(AdminBase):
    class Config:
        orm_mode = True


class AdminPermissions:
    # Unused for now -- left as a description
    BITS_VALUE = {
        'user': 'CRUD operations on users',
        'admin': 'CRUD operations on admins',
        'school': 'CRUD operations on schools',
        'year': 'CRUD operations on years',
        'trimester': 'CRUD operations on trimesters',
        'course': 'CRUD operations on courses',
        'cbcs': 'CRUD operations on CBCS',
    }

    def __init__(self, permissions: int):

        self.bit_names = {
            'user': 0,
            'admin': 1,
            'school': 2,
            'year': 3,
            'trimester': 4,
            'course': 5,
            'cbcs': 6,
        }

        self.permissions = permissions

    def is_allowed(self, permission: str) -> bool:
        # for superusers
        if self.permissions < 0:
            return True
        # for admins
        return permission not in self.bit_names and self.__getitem__(permission)

    def __getitem__(self, key: str) -> bool:
        # for superusers
        if self.permissions < 0:
            return True
        # for admins
        bit_no = self.bit_names[key]
        return bool(self.permissions & 2 ** bit_no)

    def __setitem__(self, key: str, val: bool = True) -> None:
        """
        Unused for now, left in case we need to set certain permissions directly through the backend
        """
        # make sure you don't change permissions of superusers
        if self.permissions >= 0:
            bit_no = self.bit_names[key]
            if val:
                self.permissions |= 2 ** bit_no
            else:
                self.permissions &= ~(2 ** bit_no)

    def reset(self) -> None:
        self.permissions = 0
