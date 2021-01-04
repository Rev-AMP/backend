from typing import Any, Dict, Union

from sqlalchemy.orm import Session

from app.crud.base import CRUDBase
from app.models.users.admin import Admin
from app.schemas.users.admin import AdminCreate, AdminUpdate


class CRUDAdmin(CRUDBase[Admin, AdminCreate, AdminUpdate]):
    def create(self, db: Session, *, obj_in: AdminCreate) -> Admin:
        db_obj = Admin(user_id=obj_in.user_id, permissions=obj_in.permissions)
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def update(self, db: Session, *, db_obj: Admin, obj_in: Union[AdminUpdate, Dict[str, Any]]) -> Admin:
        if isinstance(obj_in, dict):
            update_data = obj_in
        else:
            update_data = obj_in.dict(exclude_unset=True)
        return super().update(db, db_obj=db_obj, obj_in=update_data)


admin = CRUDAdmin(Admin)
