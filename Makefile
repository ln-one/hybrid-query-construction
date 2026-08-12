.PHONY: setup tiny test lint verify tables

setup:
	uv sync --extra dev

tiny:
	uv run hqc tiny --output artifacts/results/aggregated/tiny.json

test:
	uv run pytest

lint:
	uv run ruff check .

tables:
	uv run hqc report --input artifacts/results/raw --output report

verify: test lint
	uv run hqc verify --root .

