from typing import TYPE_CHECKING, Optional

from jose import jwt
from passlib.context import CryptContext
from whenever import Instant, minutes

from .settings import (
    ACCESS_TOKEN_EXPIRE_MINUTES,
    ALGORITHM,
    JWT_REFRESH_SECRET_KEY,
    JWT_SECRET_KEY,
    REFRESH_TOKEN_EXPIRE_MINUTES,
)

if TYPE_CHECKING:
    from datetime import datetime

password_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def get_hashed_password(password: str) -> str:
    return password_context.hash(password)


def verify_password(password: str, hashed_pass: str) -> bool:
    return password_context.verify(password, hashed_pass)


def create_access_token(
    subject: str, expires_delta: Optional[int] = None
) -> str:
    if expires_delta is not None:
        expires_date = Instant.now() + minutes(expires_delta)

    else:
        expires_date = Instant.now() + minutes(ACCESS_TOKEN_EXPIRE_MINUTES)

    to_encode: dict[str, datetime | str] = {
        "exp": expires_date.py_datetime(),
        "sub": subject,
    }
    return jwt.encode(to_encode, JWT_SECRET_KEY, ALGORITHM)


def create_refresh_token(
    subject: str, expires_delta: Optional[int] = None
) -> str:
    if expires_delta is not None:
        expires_date = Instant.now() + minutes(expires_delta)
    else:
        expires_date = Instant.now() + minutes(REFRESH_TOKEN_EXPIRE_MINUTES)

    to_encode: dict[str, datetime | str] = {
        "exp": expires_date.py_datetime(),
        "sub": subject,
    }
    return jwt.encode(to_encode, JWT_REFRESH_SECRET_KEY, ALGORITHM)
