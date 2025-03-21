set shell := ["powershell", "-c"]

default: format lint type_check

dev:
    uv run fastapi dev src/main.py

serve:
    uv run fastapi run src/main.py

make_migration message:
    uv run alembic revision --autogenerate -m {{ message }}

migrate:
    uv run alembic upgrade head

revert count:
    uv run alembic downgrade {{ count }}

lint:
    ruff check --fix

format:
    ruff format

type_check:
    uv run mypy . --ignore-missing-imports

deploy:
    docker-compose up --build
