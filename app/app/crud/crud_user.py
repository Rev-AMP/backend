import logging
from typing import Any, Optional, Sequence

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.security import get_password_hash, verify_password
from app.crud import admin, professor, student
from app.crud.base import CRUDBase
from app.models import User
from app.schemas import (
    AdminCreate,
    ProfessorCreate,
    StudentCreate,
    UserCreate,
    UserUpdate,
)


class CRUDUser(CRUDBase[User, UserCreate, UserUpdate]):
    def get_by_email(self, db: Session, *, email: str) -> Optional[User]:
        return db.scalars(select(User).filter_by(email=email).limit(1)).first()

    def create(self, db: Session, *, obj_in: UserCreate) -> User:
        db_obj = User(
            email=obj_in.email,
            hashed_password=get_password_hash(obj_in.password),
            full_name=obj_in.full_name,
            type=obj_in.type,
            is_admin=obj_in.is_admin or obj_in.type in ("admin", "superuser"),
            school_id=obj_in.school_id,
        )
        db.add(db_obj)
        try:
            db.commit()
        except Exception as e:
            logging.error(f"{e.__class__} - {e.__str__}")
            db.rollback()
        db.refresh(db_obj)

        # Ensure user gets the appropriate permissions depending on type
        if obj_in.type == "superuser":
            admin.create(db, obj_in=AdminCreate(user_id=db_obj.id, permissions=-1))
        elif obj_in.type == "admin" or obj_in.is_admin:
            admin.create(db, obj_in=AdminCreate(user_id=db_obj.id, permissions=0))
        elif obj_in.type == "professor":
            professor.create(db, obj_in=ProfessorCreate(user_id=db_obj.id))
        elif obj_in.type == "student":
            student.create(db, obj_in=StudentCreate(user_id=db_obj.id))
        return db_obj

    def update(self, db: Session, *, db_obj: User, obj_in: UserUpdate | dict[str, Any]) -> User:
        if isinstance(obj_in, dict):
            update_data = obj_in
        else:
            update_data = obj_in.dict(exclude_unset=True)

        if password := update_data.get("password"):
            hashed_password = get_password_hash(password)
            del update_data["password"]
            update_data["hashed_password"] = hashed_password

        if is_admin := update_data.get("is_admin") is not None:
            if is_admin and not db_obj.is_admin:
                admin.create(db, obj_in=AdminCreate(user_id=db_obj.id, permissions=0))
            else:
                admin.remove(db, id=db_obj.id)

        return super().update(db, db_obj=db_obj, obj_in=update_data)

    def authenticate(self, db: Session, *, email: str, password: str) -> Optional[User]:
        user = self.get_by_email(db, email=email)
        if not user:
            return None
        if not verify_password(password, user.hashed_password):
            return None
        return user

    def is_active(self, user: User) -> bool:
        return user.is_active

    def is_superuser(self, user: User) -> bool:
        return user.type == "superuser"

    def get_all_students_for_school(self, db: Session, *, school_id: str) -> Sequence[User]:
        return db.scalars(select(User).filter_by(type="student").filter_by(school_id=school_id)).all()

    def get_all_professors_for_school(self, db: Session, *, school_id: str) -> Sequence[User]:
        return db.scalars(select(User).filter_by(type="professor").filter_by(school_id=school_id)).all()


user = CRUDUser(User)
