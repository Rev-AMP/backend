import decouple
from sqlalchemy import Boolean, Column, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

from app.models import School

if decouple.config("DB", default="mysql") == "mysql":
    from sqlalchemy.dialects.mysql import ENUM
else:
    from sqlalchemy.dialects.postgresql import ENUM  # type: ignore

from app.db.base_class import Base


class User(Base):
    id = Column(Integer, primary_key=True, index=True)
    full_name = Column(String(100), index=True)
    email = Column(String(100), unique=True, index=True, nullable=False)
    profile_picture = Column(String(41), default=None, nullable=True)
    hashed_password = Column(String(100), nullable=False)
    is_active = Column(Boolean(), default=True)
    is_admin = Column(Boolean(), default=False)
    type = Column(ENUM("superuser", "student", "professor", "admin", name="user_type"), nullable=False)
    school_id = Column(
        Integer, ForeignKey(f"{School.__table__.name}.id", ondelete="CASCADE"), index=True, nullable=True
    )
    school = relationship("School")
