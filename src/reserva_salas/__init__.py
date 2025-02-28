import uvicorn

from .app import app

__version__ = "0.1.1"


def main() -> None:
    uvicorn.run(app, port=8080)
