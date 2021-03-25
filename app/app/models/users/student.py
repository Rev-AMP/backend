from sqlalchemy import Column, ForeignKey, Integer
from sqlalchemy.orm import relationship

from app.db.base_class import Base
from app.models.term import Term
from app.models.users.user import User


class Student(Base):
    user_id = Column(
        Integer,
        ForeignKey(f'{User.__table__.name}.id', ondelete='CASCADE'),
        index=True,
        primary_key=True,
        nullable=False,
    )
    user = relationship("User")
    term_id = Column(Integer, ForeignKey(f'{Term.__table__.name}.id', ondelete='CASCADE'), index=True, nullable=True)
    term = relationship("Term")
