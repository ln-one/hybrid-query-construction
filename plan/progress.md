# Progress

Current stage: S3 Experiments.

## Stage status

- [x] Scope and protocol decisions recorded.
- [ ] D0 experiment protocol locked.
- [x] D1 method--experiment traceability drafted and mechanically testable.
- [x] D2 table and figure contracts drafted.
- [x] Independent implementation passes tiny fixture.
- [ ] Development validation passes.
- [ ] Pre-held-out lock written.
- [ ] Held-out generation and retrieval complete.
- [ ] Evaluation and robustness analyses complete.
- [ ] Clean-room verification complete.
- [ ] Chinese report complete.

## Capability-use audit

- Required skills: experiment-results-planning, research-paper-sprint,
  paper-orchestration, verification.
- Skills actually used: experiment-results-planning, research-paper-sprint,
  paper-orchestration, verification.
- Inputs consumed: author-approved formal experiment plan and local pilot provenance.
- Inputs not used: private production code is excluded by design.
- Artifacts produced: private repository, frozen configuration schema, strict
  generation records, independent Dense/Sparse construction, compact full-ranking
  store, complete WRRF, stopping-depth replay, per-query evaluator, reporting shell.
- Verification run: 18 tests, lint, repository verifier and tiny end-to-end fixture
  passed before the formal runner was added; the expanded suite is rerun at each gate.
- Remaining risk: long local 7B generation and exact-ranking runtime.
