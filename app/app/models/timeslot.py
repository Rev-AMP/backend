from sqlalchemy import Column, String, Time, UniqueConstraint

from app.db.base_class import Base
from app.utils import generate_uuid


class TimeSlot(Base):
    id = Column(String(36), primary_key=True, default=generate_uuid)
    start_time = Column(Time)
    end_time = Column(Time)

    __table_args__ = (UniqueConstraint("start_time", "end_time", name="unique_start_end_timeslot"),)
