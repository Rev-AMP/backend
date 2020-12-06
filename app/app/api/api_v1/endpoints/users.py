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
    current_user: models.User = Depends(deps.get_current_active_superuser),
) -> Any:
    """
    Retrieve users.
    :param db: SQLAlchemt Session object pointing to the project database
    :param skip: how many initial users to skip
    :param limit: maximum number of users to fetch
    :param current_user: currently active superuser logged in
    :return: list of users
    """
    users = crud.user.get_multi(db, skip=skip, limit=limit)
    return users


@router.post("/", response_model=schemas.User)
def create_user(
    *,
    db: Session = Depends(deps.get_db),
    user_in: schemas.UserCreate,
    current_user: models.User = Depends(deps.get_current_active_superuser),
) -> Any:
    """
    Create new user.
    :param db: SQLAlchemt Session object pointing to the project database
    :param user_in: User object to be stored in DB
    :param current_user: currently active superuser logged in
    :return: User object that has been stored in DB
    """
    # check if the user already exists; raise exception code 400 if it does
    user = crud.user.get_by_email(db, email=user_in.email)
    if user:
        raise HTTPException(
            status_code=400,
            detail="The user with this username already exists in the system.",
        )

    # create new user
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
    :param db: SQLAlchemt Session object pointing to the project database
    :param password:  (new) password of the user
    :param full_name: (new) full name of the user
    :param email: (new) email of the User
    :param current_user: Currently logged in User who is to be updated
    :return: updated User object
    """
    # create a UserUpdate object to update info in
    current_user_data = jsonable_encoder(current_user)
    user_in = schemas.UserUpdate(**current_user_data)

    # update info given
    # TODO: need to update profile picture, and maybe type
    if password is not None:
        user_in.password = password
    if full_name is not None:
        user_in.full_name = full_name
    if email is not None:
        user_in.email = email

    user = crud.user.update(db, db_obj=current_user, obj_in=user_in)  # use the object to update user in db

    return user


@router.get("/me", response_model=schemas.User)
def read_user_me(
    db: Session = Depends(deps.get_db),
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Get current user.
    :param db: SQLAlchemt Session object pointing to the project database
    :param current_user: User currently logged in
    :return: User object for user currently logged in
    """
    return current_user


@router.post("/open", response_model=schemas.User)
def create_user_open(
    *,
    db: Session = Depends(deps.get_db),
    password: str = Body(...),
    email: EmailStr = Body(...),
    user_type: str = Body(...),
    full_name: str = Body(None),
    profile_picture: str = Body(None),
) -> Any:
    """
    Create new user without the need to be logged in.
    :param db: SQLAlchemt Session object pointing to the project database
    :param password: password of new User
    :param email: email of new User
    :param user_type: type of new User
    :param full_name: full name of new User
    :param profile_picture: profile picture of new User
    :return:
    """
    # check if open registration is available
    if not settings.USERS_OPEN_REGISTRATION:
        raise HTTPException(
            status_code=403,
            detail="Open user registration is forbidden on this server",
        )

    # check if user exists
    user = crud.user.get_by_email(db, email=email)
    if user:
        raise HTTPException(
            status_code=400,
            detail="The user with this username already exists in the system",
        )

    # create new User using the UserCreate object and save it in db
    user_in = schemas.UserCreate(
        password=password, email=email, type=user_type, full_name=full_name, profile_picture=profile_picture
    )
    user = crud.user.create(db, obj_in=user_in)

    return user


@router.get("/{user_id}", response_model=schemas.User)
def read_user_by_id(
    user_id: int,
    current_user: models.User = Depends(deps.get_current_active_user),
    db: Session = Depends(deps.get_db),
) -> Any:
    """
    Get a specific user by id.
    :param user_id: ID of the User to be fetched
    :param current_user: User who is currently logged in
    :param db: SQLAlchemt Session object pointing to the project database
    :return: User object corresponding to given ID
    """
    user = crud.user.get(db, id=user_id)  # fetch User from db

    # return the fetched object without checking perms if current_user is trying to fetch itself
    if user == current_user:
        return user

    # rasie exception if fetched User is not the current_user and the current_user is not a superuser
    if not crud.user.is_superuser(current_user):
        raise HTTPException(status_code=400, detail="The user doesn't have enough privileges")

    return user


@router.put("/{user_id}", response_model=schemas.User)
def update_user(
    *,
    db: Session = Depends(deps.get_db),
    user_id: int,
    user_in: schemas.UserUpdate,
    current_user: models.User = Depends(deps.get_current_active_superuser),
) -> Any:
    """
    Update a user.
    :param db: SQLAlchemt Session object pointing to the project database
    :param user_id: ID of the User to be updated
    :param user_in: UserUpdate object describing new User to be stored in db
    :param current_user: superuser currently logged in
    :return: updated User object
    """
    # fetch existing User object from db
    user = crud.user.get(db, id=user_id)
    if not user:
        raise HTTPException(
            status_code=404,
            detail="The user with this username does not exist in the system",
        )

    # save updated object based on given UserUpdate object in db
    user = crud.user.update(db, db_obj=user, obj_in=user_in)

    return user
