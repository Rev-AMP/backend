from sqlalchemy import Boolean, Column, ForeignKey, String
from sqlalchemy.dialects.postgresql import ENUM
from sqlalchemy.orm import Mapped, relationship

from app.db.base_class import Base, IDMixin
from app.models.school import School


class User(Base, IDMixin):
    full_name: Mapped[str] = Column(String, index=True)
    email: Mapped[str] = Column(String, unique=True, index=True, nullable=False)
    profile_picture: Mapped[str] | None = Column(String, default=None, nullable=True)
    hashed_password: Mapped[str] = Column(String, nullable=False)
    is_active: Mapped[bool] = Column(Boolean, default=True)
    is_admin: Mapped[bool] = Column(Boolean, default=False)
    type: Mapped[str] = Column(ENUM("superuser", "student", "professor", "admin", name="user_type"), nullable=False)
    school_id: Mapped[str] | None = Column(ForeignKey("schools.id", ondelete="CASCADE"), index=True, nullable=True)
    school: School | None = relationship("School")
