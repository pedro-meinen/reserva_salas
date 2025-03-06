from functools import wraps
from typing import Any, Callable

from fastapi import HTTPException, Request, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jose import jwt
from jose.exceptions import JWTError
from sqlmodel import select

from .models import Token
from .settings import ALGORITHM, JWT_SECRET_KEY


def decode_jwt(jwt_token: str):
    try:
        return jwt.decode(jwt_token, JWT_SECRET_KEY, ALGORITHM)
    except JWTError:
        return None


class JWTBearer(HTTPBearer):
    def __init__(
        self,
        *,
        bearer_format: str | None = None,
        scheme_name: str | None = None,
        description: str | None = None,
        auto_error: bool = True,
    ):
        super().__init__(
            bearerFormat=bearer_format,
            scheme_name=scheme_name,
            description=description,
            auto_error=auto_error,
        )

    async def __call__(self, request: Request) -> HTTPAuthorizationCredentials:
        credentials = await super().__call__(request)

        if credentials:
            if not credentials.scheme == "Bearer":
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Invalid authentication scheme.",
                )
            if not self.verify_jwt(credentials.credentials):
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Invalid token or expired token.",
                )

            return credentials
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Invalid authorization code.",
        )

    def verify_jwt(self, jwt_token: str) -> bool:
        is_token_valid = False

        try:
            payload = decode_jwt(jwt_token)
        except Exception:
            payload = None
        if payload:
            is_token_valid = True

        return is_token_valid


def token_required(func: Callable[..., Any]):
    @wraps(func)
    def wrapper(*args: Any, **kwargs: Any):
        payload = jwt.decode(kwargs["dependencies"], JWT_SECRET_KEY, ALGORITHM)
        user_id = payload["sub"]
        data = (
            kwargs["session"]
            .exec(
                select(Token).filter_by(
                    user_id=user_id,
                    access_toke=kwargs["dependencies"],
                    status=True,
                )
            )
            .first()
        )
        if data:
            return func(kwargs["dependencies"], kwargs["session"])

        return {"mensagem": "Token Bloqueado"}

    return wrapper
