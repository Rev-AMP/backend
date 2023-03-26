from sqlalchemy import Column, ForeignKey, String
from sqlalchemy.ext.associationproxy import association_proxy
from sqlalchemy.orm import Mapped, relationship

from app.db.base_class import Base
from app.models.term import Term
from app.models.users.user import User


class Student(Base):
    user_id: Mapped[str] = Column(
        String(36),
        ForeignKey("users.id", ondelete="CASCADE"),
        index=True,
        primary_key=True,
    )
    user: User = relationship("User")
    term_id: Mapped[str] | None = Column(
        String(36), ForeignKey("terms.id", ondelete="CASCADE"), index=True, nullable=True
    )

    term: Term | None = relationship("Term", back_populates="students")
    divisions: list["Division"] = association_proxy("student_division", "division")
