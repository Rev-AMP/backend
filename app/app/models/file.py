from sqlalchemy import Column, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, relationship

from app.db.base_class import Base, IDMixin
from app.models.course import Course
from app.models.users.user import User


class File(Base, IDMixin):
    course_id: Mapped[str] = Column(
        String(36), ForeignKey("courses.id", ondelete="CASCADE"), index=True, nullable=False
    )
    owner_id: Mapped[str] = Column(String(36), ForeignKey("users.id", ondelete="CASCADE"), index=True, nullable=False)
    filename: Mapped[str] = Column(String(41), unique=True, nullable=False)
    file_type: Mapped[str] = Column(String(10), nullable=False)
    submission_id: Mapped[str] | None = Column(String(36), ForeignKey("files.id", ondelete="CASCADE"), nullable=True)
    marks: Mapped[int] | None = Column(Integer, nullable=True)
    description: Mapped[str] = Column(Text, nullable=False)
    owner: User = relationship("User")
    course: Course = relationship("Course")
