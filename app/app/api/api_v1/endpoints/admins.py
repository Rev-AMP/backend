import logging
from typing import Any, List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app import crud, models, schemas
from app.api import deps

router = APIRouter()


@router.get("/", response_model=List[schemas.Admin])
def read_admins(
    db: Session = Depends(deps.get_db),
    skip: int = 0,
    limit: int = 100,
    _: models.Admin = Depends(deps.get_current_active_admin_with_permission("admin")),
) -> Any:
    """
    Retrieve admins
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


@router.get("/{admin_id}", response_model=schemas.Admin)
def read_admin_by_id(
    admin_id: int, current_admin: models.Admin = Depends(deps.get_current_admin), db: Session = Depends(deps.get_db)
) -> Any:
    """
    Get a specific admin by ID.
    """

    # Fetch Admin with the corresponding ID from DB
    admin = crud.admin.get(db, id=admin_id)

    # Return the fetched object without checking perms if current_admin is trying to fetch itself
    if admin == current_admin:
        return admin

    # check perms and return if admin exists, else 404
    if schemas.AdminPermissions(current_admin.permissions).is_allowed("admin"):
        if admin:
            return admin
        raise HTTPException(
            status_code=404,
            detail="The admin with this ID does not exist in the system",
        )

    raise HTTPException(status_code=403, detail="The user doesn't have enough privileges")


@router.put("/", response_model=schemas.Admin)
def update_admin(
    *,
    db: Session = Depends(deps.get_db),
    admin_in: schemas.AdminUpdate,
    current_admin: models.Admin = Depends(deps.get_current_active_admin_with_permission("admin")),
) -> Any:
    """
    Update admin.
    """

    if admin := crud.admin.get(db, admin_in.user_id):
        logging.info(
            f"Admin {current_admin.user_id} ({current_admin.user.email}) is updating Admin {admin.user_id} ({admin.user.email}) to {admin_in.__dict__}"
        )
        return crud.admin.update(db, db_obj=admin, obj_in=admin_in)

    raise HTTPException(
        status_code=404,
        detail="This admin does not exist!",
    )
