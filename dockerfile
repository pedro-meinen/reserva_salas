FROM python:3.12-slim-bookworm
COPY --from=ghcr.io/astral-sh/uv:0.6.9 /uv /uvx /bin/

ENV UV_COMPILE_BYTECODE=1

ADD . /app

WORKDIR /app
RUN uv sync --frozen

CMD ["uv", "run", "fastapi", "run", "src/main.py"]