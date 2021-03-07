from sqlalchemy import Column, ForeignKey, Integer

from app.db.base_class import Base
from app.models.users.user import User


class Admin(Base):
    user_id = Column(Integer, ForeignKey(f'{User.__table__.name}.id', ondelete='CASCADE'), primary_key=True, index=True)
    permissions = Column(Integer, nullable=False, default=0)
