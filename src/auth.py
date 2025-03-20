from authx import AuthX, AuthXConfig
from authx import AuthXDependency as AuthXDependency
from authx import TokenPayload as TokenPayload
from environs import env
from passlib.context import CryptContext

env.read_env(".env")

config = AuthXConfig(
    JWT_ALGORITHM="HS256",
    JWT_SECRET_KEY=env.str("JWT_SECRET_KEY"),
    JWT_TOKEN_LOCATION=["headers"],
)

auth: AuthX[object] = AuthX(config)

password_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def get_hashed_password(password: str) -> str:
    return password_context.hash(password)


def verify_password(password: str, hashed_pass: str) -> bool:
    return password_context.verify(password, hashed_pass)
