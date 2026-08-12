#!/bin/sh
set -eu

repo_root=$(CDPATH= cd -- "$(dirname -- "$0")/.." && pwd)
cd "$repo_root"

datasets="scifact nfcorpus trec-covid fiqa arguana webis-touche2020 scidocs"
for dataset in $datasets; do
  uv run hqc generate --dataset "$dataset" \
    --prompt prompts/primary-reference-v1.txt \
    --output "artifacts/generations/bridge/$dataset.jsonl"
  uv run hqc generate --dataset "$dataset" \
    --prompt prompts/baselines/mugi-v1.txt \
    --output "artifacts/generations/mugi/$dataset.jsonl"
  uv run hqc generate --dataset "$dataset" --reference-count 1 \
    --prompt prompts/baselines/query2doc-v1.txt \
    --output "artifacts/generations/query2doc/$dataset.jsonl"
done

uv run hqc generate --dataset fiqa --reference-count 1 \
  --prompt prompts/baselines/hyde-fiqa-v1.txt \
  --output artifacts/generations/hyde/fiqa.jsonl
uv run hqc generate --dataset arguana --reference-count 1 \
  --prompt prompts/baselines/hyde-arguana-v1.txt \
  --output artifacts/generations/hyde/arguana.jsonl
for dataset in scifact nfcorpus trec-covid webis-touche2020 scidocs; do
  uv run hqc generate --dataset "$dataset" --reference-count 1 \
    --prompt prompts/baselines/hyde-v1.txt \
    --output "artifacts/generations/hyde/$dataset.jsonl"
done
