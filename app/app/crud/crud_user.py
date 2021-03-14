from typing import Any, Dict, Optional, Union

from sqlalchemy.orm import Session

from app.core.security import get_password_hash, verify_password
from app.crud import admin
from app.crud.base import CRUDBase
from app.models import User
from app.schemas import AdminCreate, AdminUpdate, UserCreate, UserUpdate


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
            pass

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

        if type_ := update_data.get('type'):
            if db_obj.type in ('admin', 'superuser') and type_ not in ('admin', 'superuser'):
                admin.remove(db, id=db_obj.id)
            elif type_ == 'admin' and db_obj.type != 'admin':
                if db_obj.type == 'superuser' and (admin_obj := admin.get(db, db_obj.id)):
                    admin.update(db, db_obj=admin_obj, obj_in=AdminUpdate(user_id=db_obj.id, permissions=0))
                else:
                    admin.create(db, obj_in=AdminCreate(user_id=db_obj.id, permissions=0))

            elif type_ == 'superuser' and db_obj.type != 'superuser':
                if db_obj.type == 'admin' and (admin_obj := admin.get(db, db_obj.id)):
                    admin.update(db, db_obj=admin_obj, obj_in=AdminUpdate(user_id=db_obj.id, permissions=-1))
                else:
                    admin.create(db, obj_in=AdminCreate(user_id=db_obj.id, permissions=-1))

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
