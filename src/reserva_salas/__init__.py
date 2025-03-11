import uvicorn

from .app import app

__version__ = "0.1.2"


def main() -> None:
    uvicorn.run(app, port=8080)
