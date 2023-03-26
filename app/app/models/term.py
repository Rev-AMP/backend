from datetime import date

from sqlalchemy import Boolean, Column, Date, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, relationship

from app.db.base_class import Base, IDMixin
from app.models.year import Year


class Term(Base, IDMixin):

    name: Mapped[str] = Column(String(100), index=True, nullable=False)
    year_id: Mapped[str] = Column(String(36), ForeignKey("years.id", ondelete="CASCADE"), index=True, nullable=False)
    current_year_term: Mapped[int] = Column(Integer, nullable=False)
    start_date: date = Column(Date, index=True, nullable=False)
    end_date: date | None = Column(Date, index=True, nullable=True)
    has_electives: Mapped[bool] = Column(Boolean, default=False)
    is_active: Mapped[bool] = Column(Boolean, default=True)

    year: Year = relationship("Year")
    students: list["Student"] = relationship("Student", back_populates="term")  # type: ignore
