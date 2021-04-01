from typing import TYPE_CHECKING

from sqlalchemy import Column, ForeignKey, Integer
from sqlalchemy.orm import relationship

from app.db.base_class import Base
from app.models.users.user import User

if TYPE_CHECKING:
    from app.models.division import Division


class Professor(Base):
    user_id = Column(
        Integer,
        ForeignKey(f"{User.__table__.name}.id", ondelete="CASCADE"),
        index=True,
        primary_key=True,
    )
    user = relationship("User")

    if TYPE_CHECKING:
        divisions = relationship(f"{Division.__table__.name}", back_populates="Professor")
    else:
        divisions = relationship("Division", back_populates="Professor")
