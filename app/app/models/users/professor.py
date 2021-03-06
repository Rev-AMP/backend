from sqlalchemy import Column, ForeignKey, String
from sqlalchemy.orm import relationship

from app.db.base_class import Base
from app.models.users.user import User


class Professor(Base):
    user_id = Column(
        String(36),
        ForeignKey(f"{User.__table__.name}.id", ondelete="CASCADE"),
        index=True,
        primary_key=True,
    )

    user = relationship("User")
    divisions = relationship("Division", back_populates="professor")  # type: ignore
