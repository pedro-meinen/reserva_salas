from functools import wraps
from typing import Any, Callable

from fastapi import HTTPException, Request
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jose import jwt
from jose.exceptions import JWTError
from sqlmodel import select

from reserva_salas.models import Token

from .settings import ALGORITHM, JWT_SECRET_KEY


def decode_JWT(jwtoken: str):
    try:
        payload = jwt.decode(jwtoken, JWT_SECRET_KEY, ALGORITHM)
        return payload
    except JWTError:
        return None


class JWTBearer(HTTPBearer):
    def __init__(
        self,
        *,
        bearerFormat: str | None = None,
        scheme_name: str | None = None,
        description: str | None = None,
        auto_error: bool = True,
    ):
        super(JWTBearer, self).__init__(
            bearerFormat=bearerFormat,
            scheme_name=scheme_name,
            description=description,
            auto_error=auto_error,
        )

    async def __call__(self, request: Request) -> HTTPAuthorizationCredentials:
        credentials = await super(JWTBearer, self).__call__(request)

        if credentials:
            if not credentials.scheme == "Bearer":
                raise HTTPException(
                    status_code=403, detail="Invalid authentication scheme."
                )
            if not self.verify_jwt(credentials.credentials):
                raise HTTPException(
                    status_code=403, detail="Invalid token or expired token."
                )

            return credentials
        else:
            raise HTTPException(
                status_code=403, detail="Invalid authorization code."
            )

    def verify_jwt(self, jwtoken: str) -> bool:
        isTokenValid = False

        try:
            payload = decode_JWT(jwtoken)
        except Exception:
            payload = None
        if payload:
            isTokenValid = True

        return isTokenValid


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

        else:
            return {"mensagem": "Token Bloqueado"}

    return wrapper
