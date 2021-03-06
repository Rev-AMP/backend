from datetime import datetime, timedelta
from typing import Any, Union

from jose import jwt
from passlib.context import CryptContext

from app.core.config import settings
from app.schemas.token import Token

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

ALGORITHM = "HS512"


def create_token(subject: Union[Any, str]) -> Token:
    """
    :param subject: Subject for JWT, in this case user id
    :return: Token object, containing access and refresh tokens, and the timestamp for the access token's expiry
    """
    expire = datetime.utcnow() + get_timedelta_for_type('access')
    to_encode = {"exp": expire, "sub": str(subject), "type": 'access'}
    access_token = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=ALGORITHM)
    refresh_expiry = datetime.utcnow() + get_timedelta_for_type('refresh')
    to_encode = {"exp": refresh_expiry, "sub": str(subject), "type": 'refresh'}
    refresh_token = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=ALGORITHM)
    token = Token(access_token=access_token, refresh_token=refresh_token, expiry=int(expire.timestamp()))
    return token


def get_timedelta_for_type(type_: str) -> timedelta:
    """
    :param type_: Type of access token
    :return: Expiry time for token, in minutes
    """
    if type_ == 'refresh':
        return timedelta(minutes=settings.REFRESH_TOKEN_EXPIRES_MINUTES)
    if type_ == 'access':
        return timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    return timedelta(minutes=5)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)
