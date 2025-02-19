import os

from dotenv import load_dotenv

load_dotenv()

DATABASE_URI = "sqlite:///reserva_salas.db"

ACCESS_TOKEN_EXPIRE_MINUTES = 30
REFRESH_TOKEN_EXPIRE_MINUTES = 60 * 24 * 7

ALGORITHM = os.environ.get("ALGORITHM", "")
JWT_SECRET_KEY = os.environ.get("JWT_SECRET_KEY", "")
JWT_REFRESH_SECRET_KEY = os.environ.get("JWT_REFRESH_SECRET_KEY", "")
