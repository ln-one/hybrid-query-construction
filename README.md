# DESA: Dense Expansion and Sparse Anchoring

This repository contains the code, configurations, and result records for
DESA, a channel-asymmetric query expansion method for hybrid dense--sparse
retrieval.

The repository is experiment-first. The formal evaluation covers SciFact,
NFCorpus, TREC-COVID, FiQA, ArguAna, Touché-2020, and SCIDOCS, with every
dataset receiving equal weight in macro results.

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

Generation, indexing, retrieval, and evaluation are separate, resumable commands.

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

The full command order, robustness runs, ablations, and clean rebuild are specified
in `plan/formal-runbook.md`.

After the compatibility gate, the complete resumable execution is:

```bash
make formal-freeze
make formal-report
```

The first command builds and locks the retrieval artifacts. The second verifies the
lock and rebuilds the result tables and figures.

## Outputs

The paper source is in `paper/acl2027/`. Aggregated results are in `report/`, and
the committed per-query records can be used to rebuild the tables with `make tables`.
