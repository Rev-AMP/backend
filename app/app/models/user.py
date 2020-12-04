from sqlalchemy import Boolean, Column, Integer, String
from sqlalchemy.dialects.postgresql import ENUM

from app.db.base_class import Base


class User(Base):
    id = Column(Integer, primary_key=True, index=True)
    full_name = Column(String, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    profile_picture = Column(String, default="")
    hashed_password = Column(String, nullable=False)
    is_active = Column(Boolean(), default=True)
    type = Column(ENUM("superuser", "student", "professor", "admin", name="user_type"), nullable=False)
