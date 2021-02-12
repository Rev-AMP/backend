from sqlalchemy import Boolean, Column, Date, ForeignKey, Integer, String

from app.db.base_class import Base
from app.models.year import Year


class Term(Base):
    name = Column(String(100), index=True)
    year_id = Column(Integer, ForeignKey(f'{Year.__table__.name}.id'), primary_key=True)
    current_year_term = Column(Integer, primary_key=True)
    start_date = Column(Date, index=True, nullable=False)
    end_date = Column(Date, index=True, nullable=True)
    has_electives = Column(Boolean, default=False)
    is_active = Column(Boolean, default=True)
