from sqlalchemy import Column, ForeignKey, Integer, String, UniqueConstraint
from sqlalchemy.orm import relationship

from app.db.base_class import Base
from app.models.course import Course
from app.models.users.professor import Professor
from app.utils import generate_uuid


class Division(Base):
    id = Column(String(36), primary_key=True, index=True, default=generate_uuid)
    course_id = Column(
        String(36), ForeignKey(f"{Course.__table__.name}.id", ondelete="CASCADE"), index=True, nullable=False
    )
    division_code = Column(Integer, index=True, nullable=False)
    professor_id = Column(
        String(36), ForeignKey(f"{Professor.__table__.name}.user_id", ondelete="CASCADE"), index=True, nullable=False
    )

    course = relationship("Course")
    professor = relationship("Professor", back_populates="divisions")

    __table_args__ = (UniqueConstraint("course_id", "division_code", name="_unique_by_course_division"),)
