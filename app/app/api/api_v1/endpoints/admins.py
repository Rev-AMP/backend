from typing import Any

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app import crud, models, schemas
from app.api import deps
from app.core.config import settings
from app.utils import send_new_admin_email

router = APIRouter()


@router.get("/", response_model=schemas.Admin)
def get_admin(
    db: Session = Depends(deps.get_db),
    current_admin: models.Admin = Depends(deps.get_current_active_admin),
) -> Any:
    """
    Get current admin
    """
    return crud.admin.get(db, current_admin.id)


@router.post("/", response_model=schemas.Admin)
def create_admin(
    *,
    db: Session = Depends(deps.get_db),
    admin_in: schemas.AdminCreate,
    current_admin: models.Admin = Depends(deps.get_current_active_admin_with_permission("admin")),
) -> Any:
    """
    Create new admin.
    """
    # Check if the admin already exists; raise HTTPException with error code 400 if it does
    admin = crud.admin.get(db, id=admin_in.user_id)
    if admin:
        raise HTTPException(
            status_code=409,
            detail="This user is already an admin!",
        )

    user = crud.user.get(db, admin_in.user_id)

    # Ensure the user with the given ID exists
    if not user:
        raise HTTPException(
            status_code=404,
            detail="This user does not exist!",
        )

    # Ensure the user is a professor - others can't be made an admin
    if user.type != "professor":
        raise HTTPException(
            status_code=400,
            detail=f"A {user.type} cannot be promoted to an admin!",
        )

    # Set is_admin to true so that we don't need to change user type
    user_in = schemas.UserUpdate(id=user.id, is_admin=True)
    updated_user = crud.user.update(db, db_obj=user, obj_in=user_in)

    # Create new admin object
    admin = crud.admin.create(db, obj_in=admin_in)

    if settings.EMAILS_ENABLED:
        # Get the admin's email address
        send_new_admin_email(email_to=updated_user.email, permissions=admin_in.permissions)

    return admin


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
        return crud.admin.update(db, db_obj=admin, obj_in=admin_in)

    raise HTTPException(
        status_code=404,
        detail="This admin does not exist!",
    )


@router.delete("/", response_model=schemas.Admin)
def remove_admin(
    *,
    db: Session = Depends(deps.get_db),
    admin_in: schemas.AdminRemove,
    current_admin: models.Admin = Depends(deps.get_current_active_admin_with_permission("admin")),
) -> Any:
    """
    Delete admin i.e. demote user
    """

    # update user object
    if current_user := crud.user.get(db, admin_in.user_id):
        crud.user.update(db, db_obj=current_user, obj_in={'is_admin': False})
    else:
        raise HTTPException(
            status_code=404,
            detail="This user does not exist!",
        )

    # delete admin object
    if crud.admin.get(db, admin_in.user_id):
        return crud.admin.remove(db, id=admin_in.user_id)
    else:
        raise HTTPException(
            status_code=404,
            detail="This admin does not exist!",
        )
