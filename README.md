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
make tiny
make verify
```

- `make tiny` validates the complete pipeline on a committed synthetic fixture.
- `make tables` rebuilds tables and figures from released per-query records.
- `make verify` checks schemas, hashes, deterministic ties, replay parity, tests,
  and repository hygiene.

Formal generation, indexing, retrieval, and evaluation are separate commands so
that held-out qrels are unavailable until the pre-evaluation lock is written.

## Research boundary

The primary outcomes are retrieval quality and logical per-channel access depth.
No wall-clock latency or end-to-end speedup claim is made by this repository.

