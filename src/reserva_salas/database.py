from typing import Generator

from sqlmodel import Session, create_engine
from sqlmodel import SQLModel as SQLModel

from . import models as models
from .settings import DATABASE_URI

engine = create_engine(DATABASE_URI)


def get_session() -> Generator[Session]:
    with Session(engine) as session:
        yield session
