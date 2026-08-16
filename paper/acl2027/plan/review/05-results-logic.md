# Results review: evidence and logic

## Checks

- Fixed Top-$L$ table matches the four-dataset macro rows in
  `report/fixed-top-l-results.csv`.
- Main table matches the controlled primary macro estimates.
- Holm-adjusted claims are limited to the two preregistered comparisons.
- Shared is described as a mixed result: significant nDCG, non-significant
  corrected Recall and access differences.
- Full-method comparison is descriptive; no unregistered significance claim is
  made.
- Reference-count behavior is described as a quality/access trade-off, not a
  monotonic access trend.
- Contriever/Touch\'e is retained as the access-depth failure case.
- TREC-COVID scale reductions are described as large but non-monotonic.

## Corrections made

- Qualified the 62.23% dual-depth rate as an equal-dataset average.
- Distinguished the macro-mean depth reduction from per-dataset percentage
  aggregation.
- Removed any implication that access depth is wall-clock latency.
