# Table schema

| Table | Purpose | Rows | Metrics | Data source |
|---|---|---|---|---|
| T1 | Dataset and artifact inventory | datasets | documents, queries, qrels, hashes | manifest |
| T2 | Unified seven-dataset main result | dataset × method | nDCG@10, Recall@20, L_D, L_S, CIs | per-query records |
| T3 | Fixed Top-L dependence | L × method | quality, delta to Original, ordering | fixed-L records |
| T4 | Operator mechanism | 2×2 cells | quality, depth, support, exhaustion | factorial records |
| T5 | Robustness | generator/retriever/n | primary metrics and direction | robustness records |
| T6 | Mechanism diagnostics | dataset × channel | angle, turnover, support retention, relevant-rank movement, isolated quality/depth effects | mechanism per-query records |
| T7 | Query-level fixed-cutoff diagnostics | L × method | exact Top-20, metric changes, conclusion changes, strict reversals | `report/fixed-top-l-*.csv` |
| T8 | Functional operator controls | control pair × metric | macro quality, paired effect, CI, Holm-adjusted p | `report/operator-control-*.csv` |
| T9 | Matched QuDAR-simple baseline | dataset × method | nDCG@10, Recall@20, paired effects | `report/qudar-*.csv` |
| T10 | Main-text external comparisons with explicit subset blocks | method within seven-dataset matched-evidence or four-dataset prior-QE block | nDCG@10, Recall@20, mean accessed rank entries | `report/qudar-*.csv`, prior-method aggregates frozen in the Results artifacts |
| T11 | Per-dataset channel evidence | dataset plus cross-dataset pattern row | relative nDCG@10 changes, Dense/Sparse depth reductions, normalized Sparse support | `report/main-results.csv`, controlled primary condition |

Every aggregate row stores the source artifact hash, configuration hash, number of
queries, number of draws, aggregation rule, and bootstrap seed.
