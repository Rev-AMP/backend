from datetime import datetime, timedelta
from typing import Any, Dict, Union

from jose import jwt
from passlib.context import CryptContext

from app.core.config import settings

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

ALGORITHM = "HS512"


def create_token(subject: Union[str, Any], expires_delta: timedelta = None, type_: str = 'access') -> str:
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + get_timedelta_for_type(type_)
    to_encode = {"exp": expire, "sub": str(subject), "type": type_}
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


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


def create_access_token(subject: Union[str, Any], expires_delta: timedelta = None) -> str:
    return create_token(subject, expires_delta, type_='access')


def create_refresh_token(subject: Union[str, Any], expires_delta: timedelta = None) -> str:
    return create_token(subject, expires_delta, type_='refresh')


def create_tokens(subject: Union[str, Any]) -> Dict[str, str]:
    return {
        'access_token': create_access_token(subject, get_timedelta_for_type('access')),
        'refresh_token': create_refresh_token(subject, get_timedelta_for_type('refresh')),
    }


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)
