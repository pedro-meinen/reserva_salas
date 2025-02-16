from typing import Any, Generator

from sqlmodel import Session, create_engine

from .settings import DATABASE_URI

engine = create_engine(DATABASE_URI)


def get_session() -> Generator[Session, Any, None]:
    with Session(engine) as session:
        yield session
