#!/bin/sh
set -eu

repo_root=$(CDPATH= cd -- "$(dirname -- "$0")/.." && pwd)
cd "$repo_root"

for dataset in fiqa arguana webis-touche2020 scidocs; do
  uv run hqc generate --model robustness --dataset "$dataset" --hash-limit 100 \
    --prompt prompts/primary-reference-v1.txt \
    --output "artifacts/generations/robustness/$dataset.jsonl"
done
