from collections.abc import Generator
from typing import Any

from sqlmodel import Session, create_engine
from sqlmodel import SQLModel as SQLModel

from . import models as models
from .settings import DATABASE_URI

engine = create_engine(DATABASE_URI)


def get_session() -> Generator[Session, Any, None]:
    with Session(engine) as session:
        yield session
