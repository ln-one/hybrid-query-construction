#!/bin/sh
set -eu

repo_root=$(CDPATH= cd -- "$(dirname -- "$0")/.." && pwd)
cd "$repo_root"

directory=artifacts/generations/compat
mkdir -p "$directory"

uv run hqc generate --dataset scifact --limit 8 \
  --prompt prompts/primary-reference-v1.txt \
  --output "$directory/qwen-primary-a.jsonl"
uv run hqc generate --dataset scifact --limit 8 \
  --prompt prompts/primary-reference-v1.txt \
  --output "$directory/qwen-primary-b.jsonl"
uv run hqc generate --model robustness --dataset fiqa --limit 8 \
  --prompt prompts/primary-reference-v1.txt \
  --output "$directory/mistral-primary-a.jsonl"
uv run hqc generate --model robustness --dataset fiqa --limit 8 \
  --prompt prompts/primary-reference-v1.txt \
  --output "$directory/mistral-primary-b.jsonl"

uv run hqc generate --dataset scifact --limit 8 \
  --prompt prompts/baselines/mugi-v1.txt \
  --output "$directory/qwen-mugi-a.jsonl"
uv run hqc generate --dataset scifact --limit 8 \
  --prompt prompts/baselines/mugi-v1.txt \
  --output "$directory/qwen-mugi-b.jsonl"
uv run hqc generate --dataset scifact --limit 8 --reference-count 1 \
  --prompt prompts/baselines/query2doc-v1.txt \
  --output "$directory/qwen-query2doc-a.jsonl"
uv run hqc generate --dataset scifact --limit 8 --reference-count 1 \
  --prompt prompts/baselines/query2doc-v1.txt \
  --output "$directory/qwen-query2doc-b.jsonl"

for specification in \
  "generic nfcorpus prompts/baselines/hyde-v1.txt" \
  "fiqa fiqa prompts/baselines/hyde-fiqa-v1.txt" \
  "arguana arguana prompts/baselines/hyde-arguana-v1.txt" \
  "scifact scifact prompts/baselines/hyde-scifact-v1.txt" \
  "trec-covid trec-covid prompts/baselines/hyde-trec-covid-v1.txt"
do
  set -- $specification
  label=$1
  dataset=$2
  prompt=$3
  uv run hqc generate --dataset "$dataset" --limit 8 --reference-count 8 \
    --max-new-tokens 512 --prompt "$prompt" \
    --output "$directory/qwen-hyde-$label-a.jsonl"
  uv run hqc generate --dataset "$dataset" --limit 8 --reference-count 8 \
    --max-new-tokens 512 --prompt "$prompt" \
    --output "$directory/qwen-hyde-$label-b.jsonl"
done

uv run python scripts/verify_generation_compatibility.py \
  qwen-primary "$directory/qwen-primary-a.jsonl" "$directory/qwen-primary-b.jsonl" \
  mistral-primary "$directory/mistral-primary-a.jsonl" "$directory/mistral-primary-b.jsonl" \
  qwen-mugi "$directory/qwen-mugi-a.jsonl" "$directory/qwen-mugi-b.jsonl" \
  qwen-query2doc "$directory/qwen-query2doc-a.jsonl" "$directory/qwen-query2doc-b.jsonl" \
  qwen-hyde-generic "$directory/qwen-hyde-generic-a.jsonl" "$directory/qwen-hyde-generic-b.jsonl" \
  qwen-hyde-fiqa "$directory/qwen-hyde-fiqa-a.jsonl" "$directory/qwen-hyde-fiqa-b.jsonl" \
  qwen-hyde-arguana "$directory/qwen-hyde-arguana-a.jsonl" "$directory/qwen-hyde-arguana-b.jsonl" \
  qwen-hyde-scifact "$directory/qwen-hyde-scifact-a.jsonl" "$directory/qwen-hyde-scifact-b.jsonl" \
  qwen-hyde-trec-covid "$directory/qwen-hyde-trec-covid-a.jsonl" "$directory/qwen-hyde-trec-covid-b.jsonl"
