from sqlalchemy import Column, ForeignKey, String
from sqlalchemy.orm import Mapped, relationship

from app.db.base_class import Base
from app.models.users.user import User


class Professor(Base):
    user_id: Mapped[str] = Column(
        String(36),
        ForeignKey("users.id", ondelete="CASCADE"),
        index=True,
        primary_key=True,
    )

    user: User = relationship("User")
    divisions: list["Division"] = relationship("Division", back_populates="professor")  # type: ignore
