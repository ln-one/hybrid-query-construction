# Table schema

| Table | Purpose | Rows | Metrics | Data source |
|---|---|---|---|---|
| T1 | Dataset and artifact inventory | datasets | documents, queries, qrels, hashes | manifest |
| T2 | Held-out main result | dataset × method | nDCG@10, Recall@20, L_D, L_S, CIs | per-query records |
| T3 | Fixed Top-L dependence | L × method | quality, delta to Original, ordering | fixed-L records |
| T4 | Operator mechanism | 2×2 cells | quality, depth, support, exhaustion | factorial records |
| T5 | Robustness | generator/retriever/n | primary metrics and direction | robustness records |

Every aggregate row stores the source artifact hash, configuration hash, number of
queries, number of draws, aggregation rule, and bootstrap seed.

