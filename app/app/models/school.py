from sqlalchemy import Column, Integer, String

from app.db.base_class import Base


class School(Base):
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), unique=True, index=True, nullable=False)
    head = Column(String(100), unique=True, index=True, nullable=False)
