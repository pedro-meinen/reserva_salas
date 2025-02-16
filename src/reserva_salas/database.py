from typing import Any, Generator
from sqlmodel import Session


def get_session() -> Generator[Session, Any, None]:
    with Session() as session:
        yield session
