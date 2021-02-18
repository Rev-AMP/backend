from sqlalchemy import Boolean, Column, ForeignKey, Integer

from app.db.base_class import Base
from app.models import School


class Year(Base):
    id = Column(Integer, primary_key=True, index=True)
    school_id = Column(Integer, ForeignKey(f'{School.__table__.name}.id', ondelete='CASCADE'), index=True)
    start_year = Column(Integer, index=True)
    end_year = Column(Integer, index=True)
    is_active = Column(Boolean, default=True)
