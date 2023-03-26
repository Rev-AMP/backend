from sqlalchemy import Column, ForeignKey, Integer, String, UniqueConstraint
from sqlalchemy.ext.associationproxy import association_proxy
from sqlalchemy.orm import Mapped, relationship

from app.db.base_class import Base, IDMixin
from app.models.course import Course
from app.models.student_division import StudentDivision
from app.models.users.professor import Professor


class Division(Base, IDMixin):
    course_id: Mapped[str] = Column(
        String(36), ForeignKey("courses.id", ondelete="CASCADE"), index=True, nullable=False
    )
    division_code: Mapped[int] = Column(Integer, index=True, nullable=False)
    professor_id: Mapped[str] = Column(
        String(36), ForeignKey("professors.user_id", ondelete="CASCADE"), index=True, nullable=False
    )
    number_of_batches: Mapped[int] = Column(Integer, index=True, nullable=False)

    course: Course = relationship("Course")
    professor: Professor = relationship("Professor", back_populates="divisions")
    students: list["Student"] = association_proxy(
        "student_division",
        "student",
        creator=lambda args: StudentDivision(student=args["student"], batch_number=args["batch_number"]),
    )

    __table_args__ = (UniqueConstraint("course_id", "division_code", name="_unique_by_course_division"),)
