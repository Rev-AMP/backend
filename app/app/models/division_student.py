from sqlalchemy import Column, ForeignKey, Integer
from sqlalchemy.orm import backref, relationship

from app.db.base_class import Base
from app.models.division import Division
from app.models.users.student import Student


class StudentDivision(Base):
    student_id = (Column("student_id", Integer, ForeignKey("student.user_id", ondelete="CASCADE"), primary_key=True),)
    division_id = (Column("division_id", Integer, ForeignKey("division.id", ondelete="CASCADE"), primary_key=True),)
    batch_number = (Column("batch_number", Integer, index=True),)

    student = relationship(Student, backref=backref("student_division", cascade="all, delete-orphan"))
    division = relationship(Division, backref=backref("student_division", cascade="all, delete-orphan"))
