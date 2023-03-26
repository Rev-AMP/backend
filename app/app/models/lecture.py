from sqlalchemy import Column, ForeignKey, String
from sqlalchemy.orm import Mapped, relationship

from app.db.base_class import Base, IDMixin
from app.models.division import Division
from app.models.timeslot import TimeSlot


class Lecture(Base, IDMixin):
    day: Mapped[str] = Column(String(9), nullable=False)
    time_slot_id: Mapped[str] = Column(
        String(36), ForeignKey("timeslots.id", ondelete="CASCADE"), index=True, nullable=False
    )
    division_id: Mapped[str] = Column(
        String(36), ForeignKey("divisions.id", ondelete="CASCADE"), index=True, nullable=False
    )
    type: Mapped[str] = Column(String(9), nullable=False)
    room_number: Mapped[str] = Column(String(5))

    time_slot: TimeSlot = relationship("TimeSlot")
    division: Division = relationship("Division")
