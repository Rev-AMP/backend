from sqlalchemy import Column, ForeignKey, Integer, Table

from app.db.base_class import Base

division_student = Table(
    "division_student",
    Base.metadata,
    Column("division_id", Integer, ForeignKey("division.id", ondelete="CASCADE"), primary_key=True),
    Column("student_id", Integer, ForeignKey("student.user_id", ondelete="CASCADE"), primary_key=True),
)
