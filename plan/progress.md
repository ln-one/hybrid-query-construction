# Progress

Current stage: S5 Complete (post-held-out status record).

The experiment protocol itself remains frozen at commit
`ec605a35a22693b65ca98f7448ca2954ea6bcfed`. This file records completion after
evaluation; it does not amend any model, method, dataset, ranking, replay, metric, or
statistical decision.

## Stage status

- [x] Scope and protocol decisions recorded.
- [x] D0 experiment protocol locked.
- [x] D1 method--experiment traceability drafted and mechanically testable.
- [x] D2 table and figure contracts drafted.
- [x] Independent implementation passes tiny fixture.
- [x] Development validation passes.
- [x] Pre-held-out lock written with held-out qrels absent.
- [x] Held-out generation and retrieval complete.
- [x] Evaluation, ablation, robustness, fidelity, fixed-Top-L, and scale analyses complete.
- [x] Clean-room verification reproduces the report directory byte for byte.
- [x] Chinese report complete, including mixed and negative conditions.

## Capability-use audit

- Required skills: experiment-results-planning, research-paper-sprint,
  paper-orchestration, verification.
- Skills actually used: experiment-results-planning, research-paper-sprint,
  paper-orchestration, verification.
- Inputs consumed: author-approved formal experiment plan and local pilot provenance.
- Inputs not used: private production code is excluded by design.
- Artifacts produced: private repository, frozen configuration schema, 46,359 strict
  generation records, 19 complete-ranking stores, 665,376 query-result records,
  complete WRRF, stopping-depth replay, aggregate CSV files, figures, and `REPORT.md`.
- Verification run: 45 tests, lint, lock verification, full artifact/privacy audit,
  tiny end-to-end and reuse fixture, and a fresh `uv.lock` environment rebuild passed.
- Reported boundary: logical access depth is not wall-clock latency. The report keeps
  the mixed comparison against Bridge Shared and the negative Contriever/Touché access
  condition instead of hiding them behind the aggregate result.
