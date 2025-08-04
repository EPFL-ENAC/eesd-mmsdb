env_path=../.env

install:
	uv venv
	uv pip install -e .[dev]

run:
	uv run dotenv -f "$(env_path)" run uvicorn api.main:app --reload

test:
	uv run dotenv -f "$(env_path)" run pytest

lint:
	uv run pre-commit run --all-files
