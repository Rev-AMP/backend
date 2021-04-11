from sqlalchemy import Column, ForeignKey, String
from sqlalchemy import Column, ForeignKey, Integer
from sqlalchemy.ext.associationproxy import association_proxy
from sqlalchemy.orm import relationship

from app.db.base_class import Base
from app.models.term import Term
from app.models.users.user import User


class Student(Base):
    user_id = Column(
        String(36),
        ForeignKey(f"{User.__table__.name}.id", ondelete="CASCADE"),
        index=True,
        primary_key=True,
    )
    user = relationship("User")
    term_id = Column(String(36), ForeignKey(f"{Term.__table__.name}.id", ondelete="CASCADE"), index=True, nullable=True)

    term = relationship("Term", back_populates="students")
    divisions = association_proxy("student_division", "division")
