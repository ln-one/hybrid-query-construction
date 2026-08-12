#!/bin/sh
set -eu

repo_root=$(CDPATH= cd -- "$(dirname -- "$0")/.." && pwd)
cd "$repo_root"

directory=artifacts/generations/compat
first=$directory/qwen-scifact-batch-v3-a.jsonl
second=$directory/qwen-scifact-batch-v3-b.jsonl
mkdir -p "$directory"

uv run hqc generate --dataset scifact --limit 8 \
  --prompt prompts/primary-reference-v1.txt --output "$first"
uv run hqc generate --dataset scifact --limit 8 \
  --prompt prompts/primary-reference-v1.txt --output "$second"
uv run python scripts/verify_generation_compatibility.py "$first" "$second"
