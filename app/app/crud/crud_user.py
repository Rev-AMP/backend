from typing import Any, Dict, Optional, Union

from sqlalchemy.orm import Session

from app.core.security import get_password_hash, verify_password
from app.crud import admin, student
from app.crud.base import CRUDBase
from app.models import User
from app.schemas import AdminCreate, StudentCreate, UserCreate, UserUpdate


class CRUDUser(CRUDBase[User, UserCreate, UserUpdate]):
    def get_by_email(self, db: Session, *, email: str) -> Optional[User]:
        return db.query(User).filter(User.email == email).first()

    def create(self, db: Session, *, obj_in: UserCreate) -> User:
        db_obj = User(
            email=obj_in.email,
            hashed_password=get_password_hash(obj_in.password),
            full_name=obj_in.full_name,
            type=obj_in.type,
            is_admin=obj_in.is_admin or obj_in.type in ('admin', 'superuser'),
            school_id=obj_in.school_id,
        )
        db.add(db_obj)

        db.commit()
        db.refresh(db_obj)

        # Ensure user gets the appropriate permissions depending on type
        if obj_in.type == 'superuser':
            admin.create(db, obj_in=AdminCreate(user_id=db_obj.id, permissions=-1))
        elif obj_in.type == 'admin' or obj_in.is_admin:
            admin.create(db, obj_in=AdminCreate(user_id=db_obj.id, permissions=0))
        elif obj_in.type == 'professor':
            pass
        elif obj_in.type == 'student':
            student.create(db, obj_in=StudentCreate(user_id=db_obj.id))

        return db_obj

    def update(self, db: Session, *, db_obj: User, obj_in: Union[UserUpdate, Dict[str, Any]]) -> User:
        if isinstance(obj_in, dict):
            update_data = obj_in
        else:
            update_data = obj_in.dict(exclude_unset=True)

        if password := update_data.get("password"):
            hashed_password = get_password_hash(password)
            del update_data["password"]
            update_data["hashed_password"] = hashed_password

        if is_admin := update_data.get('is_admin') is not None:
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


user = CRUDUser(User)
