# Hybrid Query Construction

This private research repository evaluates asymmetric query construction for
hybrid dense--sparse retrieval. It is intentionally independent of EAHR,
Stratumind, Qdrant, and any private production implementation.

The repository is experiment-first. Formal claims are made only from frozen
held-out artifacts. Development results from SciFact, NFCorpus, and TREC-COVID
cannot be used as held-out evidence.

## Reproduction levels

```bash
make setup
make prepare-models
make tiny
make verify
```

- `make tiny` validates the complete pipeline on a committed synthetic fixture.
- `make tables` rebuilds tables and figures from released per-query records.
- `make verify` checks schemas, hashes, deterministic ties, replay parity, tests,
  and repository hygiene.

Formal generation, indexing, retrieval, and evaluation are separate commands so that
held-out document judgments and grades are unavailable until the pre-evaluation lock
is written. Evaluation-split query membership is prepared in advance because it
defines which public queries belong to each benchmark test set.

## Formal command boundary

Each command is resumable at query or ranking-artifact granularity:

```bash
hqc prepare --dataset scifact
hqc generate --dataset scifact --output artifacts/generations/bridge/scifact.jsonl
hqc rank --dataset scifact \
  --bridge-generation artifacts/generations/bridge/scifact.jsonl
hqc evaluate --dataset scifact \
  --store artifacts/rankings/scifact/rankings.sqlite3
```

Baseline prompts are generated into separate files and supplied to `hqc rank` with
`--mugi-generation`, `--hyde-generation`, and `--query2doc-generation`. The
reproduction cards in `plan/reproduction-cards/` state every deliberate departure
from the original papers.

The exact formal command order, qrels firewall, robustness stores, ablations, and
clean rebuild are specified in `plan/formal-runbook.md`.

## Research boundary

The primary outcomes are retrieval quality and logical per-channel access depth.
No wall-clock latency or end-to-end speedup claim is made by this repository.
