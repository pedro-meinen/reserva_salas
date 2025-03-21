from collections.abc import Generator

from environs import env
from sqlmodel import Session, create_engine
from sqlmodel import SQLModel as SQLModel

from src import models as models

env.read_env(".env")

DATABASE_URI = env.str("DATABASE_URI")

engine = create_engine(DATABASE_URI)


def get_session() -> Generator[Session]:
    with Session(engine) as session:
        yield session
