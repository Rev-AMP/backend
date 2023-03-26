from sqlalchemy import Column, ForeignKey, String, UniqueConstraint
from sqlalchemy.orm import Mapped, relationship

from app.db.base_class import Base, IDMixin
from app.models.term import Term


class Course(Base, IDMixin):
    name: Mapped[str] = Column(String(100), index=True, nullable=False)
    course_code: Mapped[str] = Column(String(20), index=True, nullable=False)
    elective_code: Mapped[str] | None = Column(String(20), index=True, nullable=True)
    term_id: Mapped[str] = Column(String(36), ForeignKey("terms.id", ondelete="CASCADE"), index=True, nullable=False)

    term: Term = relationship("Term")

    __table_args__ = (UniqueConstraint("name", "course_code", "term_id", name="_unique_by_name_code_term"),)
