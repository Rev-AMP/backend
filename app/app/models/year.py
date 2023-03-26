from sqlalchemy import Boolean, Column, ForeignKey, Integer, String, UniqueConstraint
from sqlalchemy.orm import Mapped, relationship

from app.db.base_class import Base, IDMixin
from app.models.school import School


class Year(Base, IDMixin):
    name: Mapped[str] = Column(String(100), index=True, nullable=False)
    school_id: Mapped[str] = Column(
        String(36), ForeignKey("schools.id", ondelete="CASCADE"), index=True, nullable=False
    )
    start_year: Mapped[int] = Column(Integer, index=True, nullable=False)
    end_year: Mapped[int] = Column(Integer, index=True, nullable=False)
    is_active: Mapped[bool] = Column(Boolean, default=True)

    school: Mapped[School] = relationship("School")

    __table_args__ = (UniqueConstraint("name", "school_id", "start_year", "end_year"),)
