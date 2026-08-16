# Method--experiment traceability

| Contribution | Method module | Experiment | Output | Allowed claim | Status |
|---|---|---|---|---|---|
| Top-L confounds rewrite evaluation | complete/fixed fusion | full fixed-L curve | T3/F1 | gains depend on L if observed | complete |
| Dense preserves intent while adding directions | orthogonal residual | 2x2 + residual ablation | T4 | effect attributed to residual if supported | complete |
| Sparse restricts expansion drift | score product | 2x2 + mask/product | T4/F2 | support/depth effect if supported | complete |
| Joint method improves quality | both operators | seven-dataset pooled evaluation | T2 | descriptive pooled and dataset-level effects only | complete |
| Joint method reduces logical access | replay | seven-dataset pooled evaluation | T2/F3 | stopping-depth reduction, not latency | complete |
| Effect is robust | generation/retrieval variants | robustness matrix | T5 | only tested variants | complete |
| Dense expansion is bounded in realized queries | orthogonal residual | query-angle audit | T6/F5 | observed angles satisfy the analytic bound | complete |
| Sparse anchoring changes order within the original support | score product | support and relevant-rank audit | T6/F5 | exact mathematical property; empirical retention reported separately | complete |
| Mechanism magnitude explains outcomes | both operators | quartile and correlation analysis | T6/F6 | descriptive association only; no adaptive rule | complete |
