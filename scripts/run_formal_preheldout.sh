#!/bin/sh
set -eu

repo_root=$(CDPATH= cd -- "$(dirname -- "$0")/.." && pwd)
cd "$repo_root"

make verify
uv run hqc environment --output artifacts/lock/environment-preformal.json
make prepare-models
make compatibility
make generate-qwen
make generate-robustness

for dataset in scifact nfcorpus trec-covid fiqa arguana webis-touche2020 scidocs; do
  uv run hqc rank --dataset "$dataset" \
    --bridge-generation "artifacts/generations/bridge/$dataset.jsonl" \
    --mugi-generation "artifacts/generations/mugi/$dataset.jsonl" \
    --hyde-generation "artifacts/generations/hyde/$dataset.jsonl" \
    --query2doc-generation "artifacts/generations/query2doc/$dataset.jsonl"
done

for dataset in fiqa arguana webis-touche2020 scidocs; do
  uv run hqc rank --dataset "$dataset" --run-id mistral \
    --bridge-generation "artifacts/generations/robustness/$dataset.jsonl"
  uv run hqc rank --dataset "$dataset" --run-id contriever \
    --dense-key robustness_dense \
    --bridge-generation "artifacts/generations/bridge/$dataset.jsonl"
done

for dataset in trec-covid-25000 trec-covid-50000 trec-covid-100000 trec-covid-171332; do
  uv run hqc rank --dataset "$dataset" \
    --bridge-generation artifacts/generations/bridge/trec-covid.jsonl
done

uv run hqc progress --require-complete
uv run hqc lock
