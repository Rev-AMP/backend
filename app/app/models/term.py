from sqlalchemy import Boolean, Column, Date, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

from app.db.base_class import Base
from app.models.year import Year
from app.utils import generate_uuid


class Term(Base):
    id = Column(String(36), primary_key=True, index=True, default=generate_uuid)
    name = Column(String(100), index=True, nullable=False)
    year_id = Column(
        String(36), ForeignKey(f"{Year.__table__.name}.id", ondelete="CASCADE"), index=True, nullable=False
    )
    current_year_term = Column(Integer, nullable=False)
    start_date = Column(Date, index=True, nullable=False)
    end_date = Column(Date, index=True, nullable=True)
    has_electives = Column(Boolean, default=False)
    is_active = Column(Boolean, default=True)

    year = relationship("Year")
    students = relationship("Student", back_populates="term")  # type: ignore
