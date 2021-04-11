from sqlalchemy import Column, String

from app.db.base_class import Base
from app.utils import generate_uuid


class School(Base):
    id = Column(String(36), primary_key=True, index=True, default=generate_uuid)
    name = Column(String(100), unique=True, index=True, nullable=False)
    head = Column(String(100), unique=True, index=True, nullable=False)
