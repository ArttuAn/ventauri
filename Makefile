.PHONY: install dev test lint

install:
	pip install -e ".[dev,openai]"

dev:
	uvicorn api.main:app --reload --host 127.0.0.1 --port 8000

test:
	pytest -q

lint:
	ruff check .
