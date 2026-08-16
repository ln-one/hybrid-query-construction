# Project overview

## Goal

Evaluate whether complementary generated evidence should enter Dense and Sparse
retrieval through different operators, and whether the resulting hybrid ranking
improves quality while reducing the logical ranking depth needed to certify its
own complete-list fused Top-20.

## Boundaries

- Independent repository; no EAHR, Qdrant, or Stratumind code dependency.
- Chinese result report first; no manuscript drafting in this stage.
- No online latency claim.
- Seven formal datasets are reported individually and with equal macro weight.
- Every reported value must be recoverable from per-query records.

## Frozen decisions

- Primary generator: Qwen2.5-7B-Instruct, three draws.
- Robustness generator: Mistral-7B-Instruct-v0.3, 100 hash-selected queries per selected set.
- Five references; no MuGI beta in the proposed Sparse construction.
- BGE-small Dense, Pyserini BM25 Sparse, equal complete-list WRRF with k=60.
- Formal datasets: SciFact, NFCorpus, TREC-COVID, FiQA, ArguAna, Touché-2020, SCIDOCS.
