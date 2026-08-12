# Formal experiment protocol

## Research questions

- RQ0: Does fixed Top-L change measured query-rewrite gains or method ordering?
- RQ1: Does the proposed construction improve complete-list fusion quality?
- RQ2: Does it reduce Dense and Sparse stopping depths under the frozen replay?
- RQ3: Which effects are attributable to Dense residual expansion and Sparse anchoring?
- RQ4: Are conclusions stable across datasets, draws, generators, retrievers, and reference counts?
- RQ5: How do logical access ratios change within nested snapshots of one corpus?

## Data boundary

Development only: SciFact, NFCorpus, TREC-COVID. Held-out: FiQA, ArguAna,
Touché-2020, SCIDOCS. The generation and ranking phase may read held-out queries,
their evaluation-split membership, and corpora, but not document judgments or grades.
Full qrels become available only after a lock manifest hashes code, configs, prompts,
generations, indices, and rankings.

BEIR archives can contain queries from several splits in one `queries.jsonl`. Dataset
preparation retains only query IDs present in the selected qrels split. Only this ID
membership is used before the held-out gate; document IDs and relevance grades remain
sealed in the source archive.

## Primary comparison

Original, Bridge Shared, Dense-only, Sparse-only, MuGI, HyDE, Query2doc, and the
proposed asymmetric construction. A controlled track reuses identical references;
a fidelity track uses documented published prompt and integration rules.

## Primary outcomes

nDCG@10, Recall@20, Dense stopping depth, Sparse stopping depth, channel-specific
workload-sum depth ratios, dual-depth improvement rate, Sparse support, and Sparse
exhaustion. Wall-clock latency is out of scope.

## Statistics

Three draws are nested within query. Per-query differences are first averaged over
draws. Dataset means receive equal weight in the macro result. Confidence intervals
use 10,000 stratified query bootstrap samples. Confirmatory comparisons are Proposed
versus Original and Proposed versus Bridge Shared; two-sided paired randomization
tests use 10,000 sign flips and Holm correction over the four primary endpoints per
comparator. All dataset-level estimates are also reported.

## Failure policy

Generation validates strict JSON with exactly five distinct strings. A parse failure
receives one retry with the same seed. A second failure is recorded and all generated
methods use Original for that query/draw. No failed cell is silently dropped.

Any bug discovered after qrels access increments the protocol version and reruns all
affected held-out conditions. No method, prompt, parameter, preferred draw, or dataset
may be changed in response to held-out results.

The three draws for one query are sampled together in a fixed batch of eight sorted
queries so they reuse prompt prefill. The batch seed and each draw index are stored.
Invalid draws from that batch receive one deterministic retry batch with the same seed
and validation feedback; valid draws from the initial batch are never replaced.
