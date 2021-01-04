from typing import Any, List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app import crud, models, schemas
from app.api import deps
from app.core.config import settings
from app.utils import send_new_admin_email

router = APIRouter()


@router.get("/", response_model=List[schemas.Admin])
def read_admins(
    db: Session = Depends(deps.get_db),
    skip: int = 0,
    limit: int = 100,
    current_admin: models.User = Depends(deps.get_current_active_admin),
) -> Any:
    """
    Retrieve admins.
    """
    admins = crud.admin.get_multi(db, skip=skip, limit=limit)
    return admins


@router.post("/", response_model=schemas.Admin)
def create_admin(
    *,
    db: Session = Depends(deps.get_db),
    admin_in: schemas.AdminCreate,
    current_superuser: models.User = Depends(deps.get_current_active_superuser),
) -> Any:
    """
    Create new admin.B
    """
    # Check if the admin already exists; raise HTTPException with error code 400 if it does
    admin = crud.admin.get(db, id=admin_in.user_id)
    if admin:
        raise HTTPException(
            status_code=400,
            detail="This user is already an admin!",
        )

    user = crud.user.get(db, admin_in.user_id)

    # Ensure the user with the given ID exists
    if not user:
        raise HTTPException(
            status_code=400,
            detail="This user does not exist!",
        )

    # Ensure the user is not a superuser
    if user.type == "superuser":
        raise HTTPException(
            status_code=400,
            detail="This user is a superuser!",
        )

    # Ensure the user is an admin - change type if required
    if user.type != "admin":
        user_in = schemas.UserUpdate(id=user.id, type="admin")
        # TODO: Delete user from student/professor if so required
        crud.user.update(db, db_obj=current_superuser, obj_in=user_in)

    # Create new admin
    admin = crud.admin.create(db, obj_in=admin_in)

    if settings.EMAILS_ENABLED:
        # Get the admin's email address
        if user := crud.user.get(db, admin_in.user_id):
            send_new_admin_email(email_to=user.email, permissions=admin_in.permissions)

    return admin


@router.put("/", response_model=schemas.Admin)
def update_admin(
    *,
    db: Session = Depends(deps.get_db),
    admin_in: schemas.AdminUpdate,
    current_superuser: models.User = Depends(deps.get_current_active_superuser),
) -> Any:
    """
    Update admin.
    """

    if current_admin := crud.admin.get(db, admin_in.user_id):
        return crud.admin.update(db, db_obj=current_admin, obj_in=admin_in)

    raise HTTPException(
        status_code=400,
        detail="This admin does not exist!",
    )


@router.get("/me", response_model=schemas.Admin)
def read_admin_me(
    db: Session = Depends(deps.get_db),
    current_admin: models.User = Depends(deps.get_current_active_admin),
) -> Any:
    """
    Get current admin
    """
    return current_admin


@router.get("/{admin_id}", response_model=schemas.Admin)
def read_admin_by_id(
    admin_id: int,
    current_user: models.User = Depends(deps.get_current_active_user),
    db: Session = Depends(deps.get_db),
) -> Any:
    """
    Get a specific admin by id.
    """

    # Fetch User with the corresponding id from db
    if admin := crud.admin.get(db, id=admin_id):

        # Return the fetched object without checking perms if current_admin is trying to fetch itself
        if admin.user_id == current_user.id or current_user.type == "superuser":
            return admin

    # Raise exception if fetched User is not the current_admin and the current_admin doesn't have permissions
    # TODO: Add check for admin permissions
    # if not crud.admin.is_superuser(current_admin):
    #    raise HTTPException(status_code=400, detail="The admin doesn't have enough privileges")

    return admin
