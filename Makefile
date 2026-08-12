.PHONY: setup tiny test lint verify tables clean-rebuild generate-qwen generate-robustness prepare-models compatibility formal-preheldout formal-evaluate

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

clean-rebuild:
	./scripts/clean_rebuild.sh

generate-qwen:
	./scripts/run_qwen_generation.sh

generate-robustness:
	./scripts/run_robustness_generation.sh

prepare-models:
	uv run hqc prepare-model --model primary
	uv run hqc prepare-model --model robustness

compatibility:
	./scripts/run_generation_compatibility.sh

formal-preheldout:
	./scripts/run_formal_preheldout.sh

formal-evaluate:
	./scripts/run_formal_evaluation.sh

verify: test lint
	uv run hqc verify --root .
