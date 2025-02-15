from typing import Any, Generator
from sqlmodel import Session, create_engine, SQLModel

from .settings import DATABASE_URL

engine = create_engine(DATABASE_URL)

def init_db() -> None:
    SQLModel.metadata.create_all(engine)

def get_session() -> Generator[Session, Any, None]:
    with Session() as session:
        yield session