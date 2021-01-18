from typing import Callable, Generator

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import jwt
from pydantic import ValidationError
from sqlalchemy.orm import Session

from app import crud, models, schemas
from app.core import security
from app.core.config import settings
from app.db.session import SessionLocal

reusable_oauth2 = OAuth2PasswordBearer(tokenUrl=f"{settings.API_V1_STR}/login/access-token")


def get_db() -> Generator:
    try:
        db = SessionLocal()
        yield db
    finally:
        db.close()


def get_current_user(db: Session = Depends(get_db), token: str = Depends(reusable_oauth2)) -> models.User:
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[security.ALGORITHM])
        token_data = schemas.TokenPayload(**payload)
    except (jwt.JWTError, ValidationError):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Could not validate credentials",
        )
    user = crud.user.get(db, id=token_data.sub)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user


def get_current_admin(db: Session = Depends(get_db), token: str = Depends(reusable_oauth2)) -> models.Admin:
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[security.ALGORITHM])
        token_data = schemas.TokenPayload(**payload)
    except (jwt.JWTError, ValidationError):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Could not validate credentials",
        )
    user = crud.user.get(db, id=token_data.sub)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    if not user.is_admin:
        raise HTTPException(status_code=400, detail="User is not an administrator")
    if admin := crud.admin.get(db, id=user.id):
        return admin
    raise HTTPException(status_code=404, detail="Admin object not found")


def get_current_active_user(
    current_user: models.User = Depends(get_current_user),
) -> models.User:
    if not crud.user.is_active(current_user):
        raise HTTPException(status_code=409, detail="Inactive user")
    return current_user


def get_current_active_admin(
    current_user: models.User = Depends(get_current_user),
) -> models.User:
    if crud.user.check_admin(current_user):
        return current_user
    raise HTTPException(status_code=403, detail="The user doesn't have enough privileges")


def get_current_active_admin_with_permission(permission: str) -> Callable:
    """
    Return a function that checks if the current active admin has permission for given task
    """

    def inner(current_admin: models.Admin = Depends(get_current_admin)) -> models.Admin:
        if (
            schemas.AdminPermissions(current_admin.permissions).is_allowed(permission)
            or current_admin.permissions == -1
        ):
            return current_admin
        raise HTTPException(status_code=403, detail="This admin doesn't have enough privileges")

    return inner


def get_current_active_superuser(
    current_user: models.User = Depends(get_current_user),
) -> models.User:
    if not crud.user.is_superuser(current_user):
        raise HTTPException(status_code=403, detail="The user doesn't have enough privileges")
    return current_user
