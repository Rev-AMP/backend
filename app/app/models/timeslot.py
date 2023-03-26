from datetime import time

from sqlalchemy import Column, ForeignKey, String, Time, UniqueConstraint
from sqlalchemy.orm import Mapped, relationship

from app.db.base_class import Base, IDMixin
from app.models.school import School


class TimeSlot(Base, IDMixin):
    start_time: time = Column(Time)
    end_time: time = Column(Time)
    school_id: Mapped[str] = Column(
        String(36), ForeignKey("schools.id", ondelete="CASCADE"), index=True, nullable=False
    )

    school: School = relationship("School")

    __table_args__ = (UniqueConstraint("start_time", "end_time", "school_id", name="unique_start_end_school_timeslot"),)
