#!/bin/sh
set -eu

repo_root=$(CDPATH= cd -- "$(dirname -- "$0")/.." && pwd)
cd "$repo_root"

uv run hqc verify-lock
for dataset in fiqa arguana webis-touche2020 scidocs; do
  uv run hqc unseal --dataset "$dataset"
done

for dataset in scifact nfcorpus trec-covid fiqa arguana webis-touche2020 scidocs; do
  store="artifacts/rankings/$dataset/rankings.sqlite3"
  uv run hqc evaluate --dataset "$dataset" --store "$store"
  for references in 1 3; do
    uv run hqc evaluate --dataset "$dataset" --reference-count "$references" \
      --skip-fidelity --skip-fixed-top-l --store "$store"
  done
  for constant in 2 20 100; do
    uv run hqc evaluate --dataset "$dataset" --rrf-constant "$constant" \
      --skip-fidelity --skip-fixed-top-l --store "$store"
  done
done

for dataset in fiqa arguana webis-touche2020 scidocs; do
  uv run hqc evaluate --dataset "$dataset" --result-track robustness \
    --condition-id mistral \
    --skip-fidelity --skip-fixed-top-l --output-id "${dataset}-mistral" \
    --store "artifacts/rankings/$dataset/rankings-mistral.sqlite3"
  uv run hqc evaluate --dataset "$dataset" --result-track robustness \
    --condition-id contriever \
    --skip-fidelity --skip-fixed-top-l --output-id "${dataset}-contriever" \
    --store "artifacts/rankings/$dataset/rankings-contriever.sqlite3"
done

for dataset in trec-covid-25000 trec-covid-50000 trec-covid-100000 trec-covid-171332; do
  uv run hqc evaluate --dataset "$dataset" --result-track scale \
    --skip-fidelity --skip-fixed-top-l \
    --store "artifacts/rankings/$dataset/rankings.sqlite3"
done

uv run hqc report --input artifacts/results/raw --output report
make verify
make clean-rebuild
