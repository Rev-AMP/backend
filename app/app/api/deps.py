import logging
from typing import Callable, Generator

from fastapi import Depends
from fastapi.security import OAuth2PasswordBearer
from jose import ExpiredSignatureError, jwt
from pydantic import ValidationError
from sqlalchemy.orm import Session

from app import crud, models, schemas
from app.core import security
from app.core.config import settings
from app.db.session import SessionLocal
from app.exceptions import (
    BadRequestException,
    ConflictException,
    ForbiddenException,
    NotFoundException,
)

reusable_oauth2 = OAuth2PasswordBearer(tokenUrl=f"{settings.API_V1_STR}/login/access-token")


def get_db() -> Generator:
    try:
        db = SessionLocal()
        yield db
    finally:
        db.close()


def get_user_from_token(token: str, token_type: str, db: Session) -> models.User:
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[security.ALGORITHM])
        token_data = schemas.TokenPayload(**payload)
        if token_data.type != token_type:
            raise BadRequestException(
                detail="Invalid token",
            )
    except ExpiredSignatureError:
        raise ForbiddenException(detail="Token has expired")
    except (jwt.JWTError, ValidationError) as e:
        logging.error(e.__str__())
        raise ForbiddenException(
            detail="Could not validate credentials",
        )
    if user := crud.user.get(db, id=token_data.sub):
        if user.is_active:
            return user
        raise ConflictException("User account is disabled")
    raise NotFoundException(detail="User not found")


def get_current_user(db: Session = Depends(get_db), token: str = Depends(reusable_oauth2)) -> models.User:
    return get_user_from_token(token, "access", db)


def get_current_user_refresh(db: Session = Depends(get_db), token: str = Depends(reusable_oauth2)) -> models.User:
    return get_user_from_token(token, "refresh", db)


def get_current_admin(db: Session = Depends(get_db), user: models.User = Depends(get_current_user)) -> models.Admin:
    if user.is_admin:
        if admin := crud.admin.get(db, id=user.id):
            return admin
        raise NotFoundException(detail="Admin object not found")
    raise ForbiddenException(detail="User is not an administrator")


def get_current_student(db: Session = Depends(get_db), user: models.User = Depends(get_current_user)) -> models.Student:
    if user.type == "student":
        if student := crud.student.get(db, id=user.id):
            return student
        raise NotFoundException(detail="Student object not found")
    raise ForbiddenException(detail="User is not a student")


def get_current_professor(
    db: Session = Depends(get_db), user: models.User = Depends(get_current_user)
) -> models.Professor:
    if user.type == "professor":
        if professor := crud.professor.get(db, id=user.id):
            return professor
        raise NotFoundException(detail="Professor object not found")
    raise ForbiddenException(detail="User is not a professor")


def get_current_admin_with_permission(permission: str) -> Callable:
    """
    Return a function that checks if the current active admin has permission for given task
    """

    def inner(current_admin: models.Admin = Depends(get_current_admin)) -> models.Admin:
        if schemas.AdminPermissions(current_admin.permissions).is_allowed(permission):
            return current_admin
        raise ForbiddenException(detail="This admin doesn't have enough privileges")

    return inner


def get_current_superuser(
    current_user: models.User = Depends(get_current_user),
) -> models.User:
    if crud.user.is_superuser(current_user):
        return current_user
    raise ForbiddenException(detail="The user doesn't have enough privileges")
