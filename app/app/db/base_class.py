from sqlalchemy import Column, String
from sqlalchemy.orm import Mapped
from sqlalchemy.orm.decl_api import DeclarativeBase, declared_attr

from app.utils import generate_uuid


class Base(DeclarativeBase):
    # Generate __tablename__ automatically
    @declared_attr.directive
    def __tablename__(cls) -> str:
        return cls.__name__.lower() + "s"

    __allow_unmapped__ = True


class IDMixin:
    id: Mapped[str] = Column(String(36), primary_key=True, index=True, default=generate_uuid)
