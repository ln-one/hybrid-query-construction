# Formal execution runbook

This runbook is the executable boundary for `hqc-formal-v1`. Commands are run from
the repository root. Re-running generation skips completed query/draw records.
Re-running ranking accepts only the immutable run specification beside its SQLite
store.

## 0. Environment and compatibility gate

```bash
make setup
make verify
uv run hqc environment
uv run hqc generate --dataset scifact --limit 1 --draws 1 \
  --prompt prompts/primary-reference-v1.txt \
  --output artifacts/generations/compat/qwen-scifact-one-v2.jsonl
```

The compatibility artifact must report the pinned Qwen revision, BF16, MPS, all
generation attempts, and either five valid references or the registered failure.
A model-load, BF16, or memory failure stops the formal run.

## 1. Qwen generation before held-out qrels access

```bash
for dataset in scifact nfcorpus trec-covid fiqa arguana webis-touche2020 scidocs; do
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
```

## 2. Primary ranking stores

```bash
for dataset in scifact nfcorpus trec-covid fiqa arguana webis-touche2020 scidocs; do
  uv run hqc rank --dataset "$dataset" \
    --bridge-generation "artifacts/generations/bridge/$dataset.jsonl" \
    --mugi-generation "artifacts/generations/mugi/$dataset.jsonl" \
    --hyde-generation "artifacts/generations/hyde/$dataset.jsonl" \
    --query2doc-generation "artifacts/generations/query2doc/$dataset.jsonl"
done
```

Development evaluation is permitted immediately. Held-out evaluation is not.

## 3. Robustness artifacts before held-out qrels access

Mistral uses the hash-selected 100-query subset. Contriever uses the complete Qwen
primary records and a separate ranking store.

```bash
for dataset in fiqa arguana webis-touche2020 scidocs; do
  uv run hqc generate --model robustness --dataset "$dataset" --hash-limit 100 \
    --prompt prompts/primary-reference-v1.txt \
    --output "artifacts/generations/robustness/$dataset.jsonl"
  uv run hqc rank --dataset "$dataset" --run-id mistral \
    --bridge-generation "artifacts/generations/robustness/$dataset.jsonl"
  uv run hqc rank --dataset "$dataset" --run-id contriever \
    --dense-key robustness_dense \
    --bridge-generation "artifacts/generations/bridge/$dataset.jsonl"
done
```

## 4. Nested TREC-COVID scale stores

The same Qwen records are reused because every snapshot has the same queries. Each
snapshot builds its own Lucene index, so BM25 collection statistics are recomputed.

```bash
for dataset in trec-covid-25000 trec-covid-50000 trec-covid-100000 trec-covid-171332; do
  uv run hqc rank --dataset "$dataset" \
    --bridge-generation artifacts/generations/bridge/trec-covid.jsonl
done
```

## 5. Freeze and unseal

All protocol files must be committed and the working tree clean. The lock hashes
held-out corpora, queries, source archives, generation records, indices, embeddings,
and ranking stores.

```bash
make verify
uv run hqc environment
uv run hqc lock
for dataset in fiqa arguana webis-touche2020 scidocs; do
  uv run hqc unseal --dataset "$dataset"
done
```

No protocol file may change after this gate. A necessary correction increments the
protocol version and invalidates all affected held-out results.

## 6. Evaluation matrix

```bash
for dataset in fiqa arguana webis-touche2020 scidocs; do
  uv run hqc evaluate --dataset "$dataset" \
    --store "artifacts/rankings/$dataset/rankings.sqlite3"
  for references in 1 3; do
    uv run hqc evaluate --dataset "$dataset" --reference-count "$references" \
      --skip-fidelity --store "artifacts/rankings/$dataset/rankings.sqlite3"
  done
  for constant in 2 20 100; do
    uv run hqc evaluate --dataset "$dataset" --rrf-constant "$constant" \
      --skip-fidelity --store "artifacts/rankings/$dataset/rankings.sqlite3"
  done
  uv run hqc evaluate --dataset "$dataset" --result-track robustness \
    --skip-fidelity --output-id "$dataset-mistral" \
    --store "artifacts/rankings/$dataset/rankings-mistral.sqlite3"
  uv run hqc evaluate --dataset "$dataset" --result-track robustness \
    --skip-fidelity --output-id "$dataset-contriever" \
    --store "artifacts/rankings/$dataset/rankings-contriever.sqlite3"
done

for dataset in trec-covid-25000 trec-covid-50000 trec-covid-100000 trec-covid-171332; do
  uv run hqc evaluate --dataset "$dataset" --result-track scale \
    --skip-fidelity --store "artifacts/rankings/$dataset/rankings.sqlite3"
done
```

Development datasets use the same commands but stay separate from held-out tables.

## 7. Clean rebuild and report

```bash
uv run hqc report --input artifacts/results/raw --output report
make verify
```

The clean-room check creates a fresh environment from `uv.lock`, copies only locked
per-query records, rebuilds `report/`, and compares all output hashes.
