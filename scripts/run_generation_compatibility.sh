#!/bin/sh
set -eu

repo_root=$(CDPATH= cd -- "$(dirname -- "$0")/.." && pwd)
cd "$repo_root"

directory=artifacts/generations/compat
qwen_first=$directory/qwen-scifact-batch-v3-a.jsonl
qwen_second=$directory/qwen-scifact-batch-v3-b.jsonl
mistral_first=$directory/mistral-fiqa-batch-v3-a.jsonl
mistral_second=$directory/mistral-fiqa-batch-v3-b.jsonl
mkdir -p "$directory"

uv run hqc generate --dataset scifact --limit 8 \
  --prompt prompts/primary-reference-v1.txt --output "$qwen_first"
uv run hqc generate --dataset scifact --limit 8 \
  --prompt prompts/primary-reference-v1.txt --output "$qwen_second"
uv run hqc generate --model robustness --dataset fiqa --limit 8 \
  --prompt prompts/primary-reference-v1.txt --output "$mistral_first"
uv run hqc generate --model robustness --dataset fiqa --limit 8 \
  --prompt prompts/primary-reference-v1.txt --output "$mistral_second"
uv run python scripts/verify_generation_compatibility.py \
  "$qwen_first" "$qwen_second" "$mistral_first" "$mistral_second"
