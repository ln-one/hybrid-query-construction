## Task Packet

- Scope: strengthen three reviewer-sensitive parts of the DESA paper without
  changing the unified seven-dataset evaluation scope.
- Files to read: frozen reporting CSVs, ranking/evaluation code, current
  Experiments and Results sections, QuDAR paper and official implementation.
- Files allowed to edit: reporting/evaluation code and tests when a baseline can
  be reconstructed from frozen rankings; derived report artifacts; ACL
  Experiments, Results, Appendix, references, and planning records.
- Required skills: research-writing workflow, paper orchestration,
  experiment-results planning, evidence-driven writing, LaTeX output, PDF
  inspection, and verification.
- Evidence/data inputs: all seven evaluation collections, three-draw
  query-level records, fixed-cutoff results, complete Dense/Sparse ranking
  stores, and primary-source QuDAR specifications.
- Required artifacts:
  1. query-level incidence and magnitude analysis of fixed-cutoff disagreement;
  2. fair operator controls using frozen evidence where technically possible;
  3. a QuDAR baseline feasibility decision, and implementation/results if its
     four required signals are recoverable without regenerating evidence;
  4. manuscript updates only for results backed by generated artifacts.
- Rejection checks: no development/held-out split; no mock numbers; no claim of
  superiority without a matched experiment; no replacement of historical raw
  artifacts; no silent change to WRRF or generation settings.
- Validation commands: unit tests for changed code, deterministic report
  regeneration, numeric cross-checks against source CSVs, anonymous/public
  LaTeX builds, log checks, rendered-page inspection, and `git diff --check`.

### Completion status

- [x] Fixed-cutoff query--draw diagnostics generated for the unified seven
  datasets.
- [x] Dense contextual/residual and Sparse rewrite/product controls evaluated
  with query-level paired inference after averaging the three draws.
- [x] QuDAR-simple RRF reconstructed from OS/ES/OD/ED at the official Top-1000
  depth and RRF constant 60, using matched generated evidence.
- [x] Main text kept concise; detailed controls and per-dataset QuDAR values
  moved to the appendix.
- [x] Final anonymous/public build and rendered-page inspection.
