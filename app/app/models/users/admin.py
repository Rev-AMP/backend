from sqlalchemy import Column, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, relationship

from app.db.base_class import Base
from app.models.users.user import User


class Admin(Base):
    user_id: Mapped[str] = Column(String(36), ForeignKey("users.id", ondelete="CASCADE"), primary_key=True, index=True)
    permissions: Mapped[int] = Column(Integer, nullable=False, default=0)
    user: User = relationship("User")
