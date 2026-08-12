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

uv run hqc generate --dataset fiqa --reference-count 8 --max-new-tokens 512 \
  --prompt prompts/baselines/hyde-fiqa-v1.txt \
  --output artifacts/generations/hyde/fiqa.jsonl
uv run hqc generate --dataset arguana --reference-count 8 --max-new-tokens 512 \
  --prompt prompts/baselines/hyde-arguana-v1.txt \
  --output artifacts/generations/hyde/arguana.jsonl
uv run hqc generate --dataset scifact --reference-count 8 --max-new-tokens 512 \
  --prompt prompts/baselines/hyde-scifact-v1.txt \
  --output artifacts/generations/hyde/scifact.jsonl
uv run hqc generate --dataset trec-covid --reference-count 8 --max-new-tokens 512 \
  --prompt prompts/baselines/hyde-trec-covid-v1.txt \
  --output artifacts/generations/hyde/trec-covid.jsonl
for dataset in nfcorpus webis-touche2020 scidocs; do
  uv run hqc generate --dataset "$dataset" --reference-count 8 --max-new-tokens 512 \
    --prompt prompts/baselines/hyde-v1.txt \
    --output "artifacts/generations/hyde/$dataset.jsonl"
done
