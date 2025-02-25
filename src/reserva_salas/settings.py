from pathlib import Path

from environs import env

DATABASE_URI = "sqlite:///reserva_salas.db"

ACCESS_TOKEN_EXPIRE_MINUTES = 30
REFRESH_TOKEN_EXPIRE_MINUTES = 60 * 24 * 7

PROJECT_DIR = Path(__file__).parent.parent.resolve().absolute()

env.read_env(PROJECT_DIR / ".env")

ALGORITHM = env.str("ALGORITHM")
JWT_SECRET_KEY = env.str("JWT_SECRET_KEY")
JWT_REFRESH_SECRET_KEY = env.str("JWT_REFRESH_SECRET_KEY")
