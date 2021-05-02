from sqlalchemy import Column, ForeignKey, String
from sqlalchemy.orm import relationship

from app.db.base_class import Base
from app.models.division import Division
from app.models.timeslot import TimeSlot
from app.utils import generate_uuid


class Lecture(Base):
    id = Column(String(36), primary_key=True, index=True, default=generate_uuid)
    day = Column(String(9), nullable=False)
    time_slot_id = Column(
        String(36), ForeignKey(f"{TimeSlot.__table__.name}.id", ondelete="CASCADE"), index=True, nullable=False
    )
    division_id = Column(
        String(36), ForeignKey(f"{Division.__table__.name}.id", ondelete="CASCADE"), index=True, nullable=False
    )
    type = Column(String(9), nullable=False)
    room_number = Column(String(5))

    time_slot = relationship("TimeSlot")
    division = relationship("Division")
