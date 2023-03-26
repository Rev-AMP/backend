from sqlalchemy import Column, String
from sqlalchemy.orm import Mapped

from app.db.base_class import Base, IDMixin


class School(Base, IDMixin):
    name: Mapped[str] = Column(String, unique=True, index=True, nullable=False)
    head: Mapped[str] = Column(String, unique=True, index=True, nullable=False)
