from sqlalchemy import Column, ForeignKey, String

from app.db.base_class import Base
from app.models.course import Course
from app.models.users.user import User
from app.utils import generate_uuid


class File(Base):
    id = Column(String(36), primary_key=True, index=True, default=generate_uuid)
    course_id = Column(
        String(36), ForeignKey(f"{Course.__table__.name}.id", ondelete="CASCADE"), index=True, nullable=False
    )
    owner_id = Column(
        String(36), ForeignKey(f"{User.__table__.name}.id", ondelete="CASCADE"), index=True, nullable=False
    )
    filename = Column(String(41), unique=True, nullable=False)
