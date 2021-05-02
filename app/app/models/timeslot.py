from sqlalchemy import Column, ForeignKey, String, Time, UniqueConstraint
from sqlalchemy.orm import relationship

from app.db.base_class import Base
from app.models.school import School
from app.utils import generate_uuid


class TimeSlot(Base):
    id = Column(String(36), primary_key=True, default=generate_uuid)
    start_time = Column(Time)
    end_time = Column(Time)
    school_id = Column(
        String(36), ForeignKey(f"{School.__table__.name}.id", ondelete="CASCADE"), index=True, nullable=False
    )

    school = relationship("School")

    __table_args__ = (UniqueConstraint("start_time", "end_time", "school_id", name="unique_start_end_school_timeslot"),)
