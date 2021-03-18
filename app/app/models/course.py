from sqlalchemy import Column, ForeignKey, Integer, String, UniqueConstraint
from sqlalchemy.orm import relationship

from app.db.base_class import Base
from app.models.term import Term


class Course(Base):
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), index=True, nullable=False)
    code = Column(String(20), index=True, nullable=False)
    term_id = Column(Integer, ForeignKey(f'{Term.__table__.name}.id', ondelete='CASCADE'), index=True, nullable=False)

    term = relationship('Term')

    __table_args__ = (UniqueConstraint('name', 'code', 'term_id', name='_unique_by_name_code_term'),)
