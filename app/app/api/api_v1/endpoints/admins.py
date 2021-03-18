from typing import Any, List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app import crud, models, schemas
from app.api import deps

router = APIRouter()


@router.get("/", response_model=List[schemas.Admin])
def get_admin(
    db: Session = Depends(deps.get_db),
    skip: int = 0,
    limit: int = 100,
    _: models.Admin = Depends(deps.get_current_active_admin_with_permission("admin")),
) -> Any:
    """
    Get current admin
    """
    return crud.admin.get_multi(db, skip=skip, limit=limit)


@router.get("/me", response_model=schemas.Admin)
def get_admin_me(
    current_admin: models.Admin = Depends(deps.get_current_admin),
) -> Any:
    """
    Get current admin
    """
    return current_admin


@router.put("/", response_model=schemas.Admin)
def update_admin(
    *,
    db: Session = Depends(deps.get_db),
    admin_in: schemas.AdminUpdate,
    _: models.Admin = Depends(deps.get_current_active_admin_with_permission("admin")),
) -> Any:
    """
    Update admin.
    """

    if admin := crud.admin.get(db, admin_in.user_id):
        return crud.admin.update(db, db_obj=admin, obj_in=admin_in)

    raise HTTPException(
        status_code=404,
        detail="This admin does not exist!",
    )
