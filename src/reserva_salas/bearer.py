from collections.abc import Callable
from functools import wraps

from fastapi import HTTPException, Request, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jose import jwt
from jose.exceptions import JWTError
from sqlmodel import Session, select

from .models import Token
from .settings import ALGORITHM, JWT_SECRET_KEY


def decode_jwt(jwt_token: str) -> dict[str, str] | None:
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
    ) -> None:
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

    def verify_jwt(self, jwt_token: str) -> bool:  # noqa: PLR6301
        is_token_valid = False

        try:
            payload = decode_jwt(jwt_token)
        except JWTError:
            payload = None
        if payload:
            is_token_valid = True

        return is_token_valid


def token_required[**P, R](
    func: Callable[P, R],
) -> Callable[P, R | dict[str, str]]:
    @wraps(func)
    def wrapper(*args: P.args, **kwargs: P.kwargs) -> R | dict[str, str]:
        dependencies: str = str(kwargs["dependencies"])

        if isinstance(kwargs["session"], Session):
            session = kwargs["session"]
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Sessão do banco de dados não foi definida",
            )

        payload = jwt.decode(dependencies, JWT_SECRET_KEY, ALGORITHM)
        user_id = payload["sub"]
        data = session.exec(
            select(Token).where(
                Token.id_usuario == user_id,
                Token.access_token == dependencies,
                Token.status,
            )
        ).first()
        if data:
            return func(*args, **kwargs)

        return {"mensagem": "Token Bloqueado"}

    return wrapper
