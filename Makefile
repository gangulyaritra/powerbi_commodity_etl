.PHONY: init build run format format.check lint.check type.check

init:
    uv --version || curl -LsSf https://astral.sh/uv/install.sh | sh

build:
    docker build -t powerbi-commodity-etl:latest .

run:
    docker run -it --rm --env-file .env --cpus="0.5" --memory="512m" --net=host powerbi-commodity-etl:latest

format:
    uv run ruff format .

format.check:
    uv run ruff format --check .

lint.check:
    uv run ruff check .

type.check:
    uv run mypy src/powerbi_etl

test:
    uv run pytest
