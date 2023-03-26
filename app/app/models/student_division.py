from sqlalchemy import Column, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, backref, relationship

from app.db.base_class import Base, IDMixin
from app.models.users.student import Student


class StudentDivision(Base, IDMixin):
    student_id: Mapped[str] = Column(
        "student_id", String(36), ForeignKey("students.user_id", ondelete="CASCADE"), primary_key=True
    )
    division_id: Mapped[str] = Column(
        "division_id", String(36), ForeignKey("divisions.id", ondelete="CASCADE"), primary_key=True
    )
    batch_number: Mapped[int] = Column("batch_number", Integer, index=True)

    student: Student = relationship(Student, backref=backref("student_division", cascade="all, delete-orphan"))
    division: "Division" = relationship(
        "Division", backref=backref("student_division", cascade="all, delete-orphan")
    )  # type: ignore
