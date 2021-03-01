from typing import Any

from fastapi import APIRouter, Body, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from app import crud, models, schemas
from app.api import deps
from app.core.security import create_tokens, get_password_hash
from app.utils import (
    generate_password_reset_token,
    send_reset_password_email,
    verify_password_reset_token,
)

router = APIRouter()


@router.post("/login/access-token", response_model=schemas.Token)
def login_access_token(db: Session = Depends(deps.get_db), form_data: OAuth2PasswordRequestForm = Depends()) -> Any:
    """
    OAuth2 compatible token login, get an access token for future requests
    """

    if user := crud.user.authenticate(db, email=form_data.username, password=form_data.password):
        if crud.user.is_active(user):
            return create_tokens(user.id)
        raise HTTPException(status_code=400, detail="Inactive user")
    raise HTTPException(status_code=401, detail="Incorrect email or password")


@router.post("/login/refresh-token", response_model=schemas.Token)
def login_refresh_token(
    db: Session = Depends(deps.get_db), current_user: models.User = Depends(deps.get_current_user_refresh)
) -> Any:
    """
    OAuth2 compatible token login, get an access token for future requests
    """
    if user := crud.user.get(db, current_user.id):
        if crud.user.is_active(user):
            return create_tokens(user.id)
        raise HTTPException(status_code=400, detail="Inactive user")
    raise HTTPException(status_code=401, detail="Incorrect refresh token")


@router.post("/login/test-token", response_model=schemas.User)
def test_token(current_user: models.User = Depends(deps.get_current_user)) -> Any:
    """
    Test access token
    """
    return current_user


@router.post("/password-recovery/{email}", response_model=schemas.Msg)
def recover_password(email: str, db: Session = Depends(deps.get_db)) -> Any:
    """
    Password Recovery
    """
    if user := crud.user.get_by_email(db, email=email):
        password_reset_token = generate_password_reset_token(email=email)
        send_reset_password_email(email_to=user.email, email=email, token=password_reset_token)
        return {"msg": "Password recovery email sent"}
    raise HTTPException(
        status_code=404,
        detail="The user with this username does not exist in the system.",
    )


@router.post("/reset-password/", response_model=schemas.Msg)
def reset_password(
    token: str = Body(...),
    new_password: str = Body(...),
    db: Session = Depends(deps.get_db),
) -> Any:
    """
    Reset password
    """
    if email := verify_password_reset_token(token):
        if user := crud.user.get_by_email(db, email=email):
            if crud.user.is_active(user):
                hashed_password = get_password_hash(new_password)
                user.hashed_password = hashed_password
                db.add(user)
                db.commit()
                return {"msg": "Password updated successfully"}
            raise HTTPException(status_code=400, detail="Inactive user")
        raise HTTPException(
            status_code=404,
            detail="The user with this username does not exist in the system.",
        )
    raise HTTPException(status_code=400, detail="Invalid token")
