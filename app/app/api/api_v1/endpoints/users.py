from typing import Any, List

from fastapi import APIRouter, Body, Depends, HTTPException
from fastapi.encoders import jsonable_encoder
from pydantic.networks import EmailStr
from sqlalchemy.orm import Session

from app import crud, models, schemas
from app.api import deps
from app.core.config import settings
from app.utils import send_new_account_email

router = APIRouter()


@router.get("/", response_model=List[schemas.User])
def read_users(
    db: Session = Depends(deps.get_db),
    skip: int = 0,
    limit: int = 100,
    current_admin: models.Admin = Depends(deps.get_current_active_admin_with_permission("user")),
) -> Any:
    """
    Retrieve users.
    """
    users = crud.user.get_multi(db, skip=skip, limit=limit)
    return users


@router.post("/", response_model=schemas.User)
def create_user(
    *,
    db: Session = Depends(deps.get_db),
    user_in: schemas.UserCreate,
    current_admin: models.Admin = Depends(deps.get_current_active_admin_with_permission("user")),
) -> Any:
    """
    Create new user.
    """

    if current_admin_user := crud.user.get(db, current_admin.user_id):
        if user_in.type == "superuser" and not crud.user.is_superuser(current_admin_user):
            raise HTTPException(
                status_code=403,
                detail="Only superusers can create more superusers.",
            )

    # Check if the user already exists; raise HTTPException with error code 400 if it does
    user = crud.user.get_by_email(db, email=user_in.email)
    if user:
        raise HTTPException(
            status_code=409,
            detail="The user with this email already exists in the system.",
        )

    # Create new user
    user = crud.user.create(db, obj_in=user_in)
    if settings.EMAILS_ENABLED and user_in.email:
        send_new_account_email(email_to=user_in.email, username=user_in.email, password=user_in.password)

    return user


@router.put("/me", response_model=schemas.User)
def update_user_me(
    *,
    db: Session = Depends(deps.get_db),
    password: str = Body(None),
    full_name: str = Body(None),
    email: EmailStr = Body(None),
    profile_picture: str = Body(None),
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Update own user.
    """
    # Create a UserUpdate object to update info in
    current_user_data = jsonable_encoder(current_user)
    user_in = schemas.UserUpdate(**current_user_data)

    # Update info given
    if password is not None:
        user_in.password = password
    if full_name is not None:
        user_in.full_name = full_name
    if email is not None:
        user_in.email = email
    if profile_picture is not None:
        user_in.profile_picture = profile_picture

    # Use the object to update user in db
    user = crud.user.update(db, db_obj=current_user, obj_in=user_in)

    return user


@router.get("/me", response_model=schemas.User)
def read_user_me(
    db: Session = Depends(deps.get_db),
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Get current user.
    """
    return current_user


@router.get("/{user_id}", response_model=schemas.User)
def read_user_by_id(
    user_id: int,
    current_user: models.User = Depends(deps.get_current_active_user),
    db: Session = Depends(deps.get_db),
) -> Any:
    """
    Get a specific user by id.
    """

    # Fetch User with the corresponding id from db
    user = crud.user.get(db, id=user_id)

    # Return the fetched object without checking perms if current_user is trying to fetch itself
    if user == current_user:
        return user

    # Raise exception if fetched User is not the current_user and the current_user is not a superuser
    if current_user.is_admin:
        if admin := crud.admin.get(db, current_user.id):
            if schemas.AdminPermissions(admin.permissions).is_allowed("admin"):
                if user:
                    return user
                raise HTTPException(
                    status_code=404,
                    detail="The user with this ID does not exist in the system",
                )

    raise HTTPException(status_code=400, detail="The user doesn't have enough privileges")


@router.put("/{user_id}", response_model=schemas.User)
def update_user(
    *,
    db: Session = Depends(deps.get_db),
    user_id: int,
    user_in: schemas.UserUpdate,
    current_admin: models.Admin = Depends(deps.get_current_active_admin_with_permission("user")),
) -> Any:
    """
    Update a user.
    """

    # Fetch existing User object from db
    user = crud.user.get(db, id=user_id)
    if not user:
        raise HTTPException(
            status_code=404,
            detail="The user with this username does not exist in the system",
        )

    # Save updated object based on given UserUpdate object in db
    user = crud.user.update(db, db_obj=user, obj_in=user_in)

    return user
