from typing import Any, List

from fastapi import APIRouter, Body, Depends, File, HTTPException, UploadFile
from pydantic.networks import EmailStr
from sqlalchemy.orm import Session

from app import crud, models, schemas
from app.api import deps
from app.core.config import settings
from app.utils import save_image, send_new_account_email

router = APIRouter()


@router.get("/", response_model=List[schemas.User])
def read_users(
    db: Session = Depends(deps.get_db),
    skip: int = 0,
    limit: int = 100,
    _: models.Admin = Depends(deps.get_current_active_admin_with_permission("user")),
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
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Update own user.
    """
    # Create a UserUpdate object to update info in
    user_in = schemas.UserUpdate()

    # Update info given
    if password is not None:
        user_in.password = password
    if full_name is not None:
        user_in.full_name = full_name
    if email is not None:
        user_in.email = email

    # Use the object to update user in db
    user = crud.user.update(db, db_obj=current_user, obj_in=user_in)

    return user


@router.get("/me", response_model=schemas.User)
def read_user_me(
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

    raise HTTPException(status_code=403, detail="The user doesn't have enough privileges")


@router.put("/{user_id}", response_model=schemas.User)
def update_user(
    *,
    db: Session = Depends(deps.get_db),
    user_id: int,
    user_in: schemas.UserUpdate,
    _: models.Admin = Depends(deps.get_current_active_admin_with_permission("user")),
) -> Any:
    """
    Update a user.
    """

    # Fetch existing User object from db

    if user := crud.user.get(db, id=user_id):
        if user_in.type:
            raise HTTPException(status_code=400, detail="User roles cannot be changed")
        if user_in.is_admin is not None and user.type != 'professor':
            raise HTTPException(
                status_code=400,
                detail=f"A {user.type} cannot have admin roles changed!",
            )

        return crud.user.update(db, db_obj=user, obj_in=user_in)

    raise HTTPException(
        status_code=404,
        detail="The user with this id does not exist in the system",
    )


@router.put("/{user_id}/profile_picture", response_model=schemas.User)
def update_user_profile_picture(
    *,
    db: Session = Depends(deps.get_db),
    user_id: int,
    image: UploadFile = File(...),
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Update a user's profile picture
    """
    if current_user.id == user_id or (
        (admin := crud.admin.get(db, current_user.id))
        and schemas.AdminPermissions(admin.permissions).is_allowed("user")
    ):
        if image.content_type not in ("image/png", "image/jpeg"):
            raise HTTPException(status_code=415, detail="Profile pictures can only be PNG or JPG images")

        if user := crud.user.get(db, user_id):
            filename = save_image(image)
            return crud.user.update(db, db_obj=user, obj_in=schemas.UserUpdate(profile_picture=filename))

        raise HTTPException(
            status_code=404,
            detail="The user with this id does not exist in the system",
        )

    raise HTTPException(status_code=403, detail="The user doesn't have enough privileges")
