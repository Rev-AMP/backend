from sqlalchemy import Column, ForeignKey, Integer, String
from sqlalchemy.orm import backref, relationship

from app.db.base_class import Base
from app.models.users.student import Student


class StudentDivision(Base):
    student_id = Column("student_id", String(36), ForeignKey("students.user_id", ondelete="CASCADE"), primary_key=True)
    division_id = Column("division_id", String(36), ForeignKey("divisions.id", ondelete="CASCADE"), primary_key=True)
    batch_number = Column("batch_number", Integer, index=True)

    student = relationship(Student, backref=backref("student_division", cascade="all, delete-orphan"))
    division = relationship(
        "Division", backref=backref("student_division", cascade="all, delete-orphan")
    )  # type: ignore
