from sqlalchemy import Column, ForeignKey, String, UniqueConstraint
from sqlalchemy.orm import relationship

from app.db.base_class import Base
from app.models.term import Term
from app.utils import generate_uuid


class Course(Base):
    id = Column(String(36), primary_key=True, index=True, default=generate_uuid)
    name = Column(String(100), index=True, nullable=False)
    course_code = Column(String(20), index=True, nullable=False)
    elective_code = Column(String(20), index=True, nullable=True)
    term_id = Column(
        String(36), ForeignKey(f"{Term.__table__.name}.id", ondelete="CASCADE"), index=True, nullable=False
    )

    term = relationship("Term")

    __table_args__ = (UniqueConstraint("name", "course_code", "term_id", name="_unique_by_name_code_term"),)
