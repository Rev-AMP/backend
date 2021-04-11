from sqlalchemy import Column, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

from app.db.base_class import Base
from app.models.users.user import User


class Admin(Base):
    user_id = Column(
        String(36), ForeignKey(f"{User.__table__.name}.id", ondelete="CASCADE"), primary_key=True, index=True
    )
    permissions = Column(Integer, nullable=False, default=0)
    user = relationship("User")
