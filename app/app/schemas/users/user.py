from typing import Optional

from pydantic import BaseModel, EmailStr, validator

from app.schemas.school import School


# Shared properties
class UserBase(BaseModel):
    email: Optional[EmailStr] = None
    is_active: Optional[bool] = True
    type: Optional[str] = None
    full_name: Optional[str] = None
    profile_picture: Optional[str] = None
    is_admin: Optional[bool] = None
    school_id: Optional[int] = None

    @validator("type")
    def valid_type(cls, user_type: Optional[str]) -> Optional[str]:
        if user_type and user_type not in ("superuser", "student", "professor", "admin"):
            raise ValueError("Invalid user type!")
        return user_type

    @validator("password", check_fields=False)
    def valid_password(cls, password: Optional[str]) -> Optional[str]:
        if password:
            if len(password) < 8:
                raise ValueError("Password must contain atleast 8 characters!")
            digit_count = sum(c.isdigit() for c in password)
            lower_count = sum(c.islower() for c in password)
            upper_count = sum(c.isupper() for c in password)
            if digit_count < 1 or lower_count < 1 or upper_count < 1:
                raise ValueError(
                    "Password must contain atleast 1 each of upper case letters, lower case letters, and digits"
                )
        return password


# Properties to receive via API on creation
class UserCreate(UserBase):
    email: EmailStr
    password: str
    type: str
    is_admin: bool = False


# Properties to receive via API on update
class UserUpdate(UserBase):
    password: Optional[str] = None


class UserInDBBase(UserBase):
    id: Optional[int] = None

    class Config:
        orm_mode = True


# Additional properties to return via API
class User(UserInDBBase):
    school: Optional[School]


# Additional properties stored in DB
class UserInDB(UserInDBBase):
    hashed_password: str
