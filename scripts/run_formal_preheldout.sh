#!/bin/sh
set -eu

repo_root=$(CDPATH= cd -- "$(dirname -- "$0")/.." && pwd)
cd "$repo_root"

make verify
uv run hqc environment --output artifacts/lock/environment-preformal.json
make prepare-models
make compatibility
if uv run hqc check-generations --group qwen >/dev/null 2>&1; then
  echo "Qwen generation artifacts already complete; verified and reused."
else
  make generate-qwen
fi
if uv run hqc check-generations --group robustness >/dev/null 2>&1; then
  echo "Mistral generation artifacts already complete; verified and reused."
else
  make generate-robustness
fi

for dataset in scifact nfcorpus trec-covid fiqa arguana webis-touche2020 scidocs; do
  if uv run hqc check-ranking --dataset "$dataset" >/dev/null 2>&1; then
    echo "$dataset primary rankings already complete; verified and reused."
  else
    uv run hqc rank --dataset "$dataset" \
      --bridge-generation "artifacts/generations/bridge/$dataset.jsonl" \
      --mugi-generation "artifacts/generations/mugi/$dataset.jsonl" \
      --hyde-generation "artifacts/generations/hyde/$dataset.jsonl" \
      --query2doc-generation "artifacts/generations/query2doc/$dataset.jsonl"
  fi
done

for dataset in fiqa arguana webis-touche2020 scidocs; do
  primary_store="artifacts/rankings/$dataset/rankings.sqlite3"
  if uv run hqc check-ranking --dataset "$dataset" --run-id mistral >/dev/null 2>&1; then
    echo "$dataset Mistral rankings already complete; verified and reused."
  else
    uv run hqc rank --dataset "$dataset" --run-id mistral \
      --reuse-store "$primary_store" --reuse-mode base \
      --bridge-generation "artifacts/generations/robustness/$dataset.jsonl"
  fi
  if uv run hqc check-ranking --dataset "$dataset" --run-id contriever >/dev/null 2>&1; then
    echo "$dataset Contriever rankings already complete; verified and reused."
  else
    uv run hqc rank --dataset "$dataset" --run-id contriever \
      --dense-key robustness_dense \
      --reuse-store "$primary_store" --reuse-mode sparse \
      --bridge-generation "artifacts/generations/bridge/$dataset.jsonl"
  fi
done

for dataset in trec-covid-25000 trec-covid-50000 trec-covid-100000 trec-covid-171332; do
  if uv run hqc check-ranking --dataset "$dataset" >/dev/null 2>&1; then
    echo "$dataset scale rankings already complete; verified and reused."
  else
    uv run hqc rank --dataset "$dataset" --reuse-embeddings-from trec-covid \
      --bridge-generation artifacts/generations/bridge/trec-covid.jsonl
  fi
done

uv run hqc progress --require-complete
uv run hqc lock
