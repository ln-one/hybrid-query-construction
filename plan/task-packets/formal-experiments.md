# Task packet — formal experiments

- Scope: implement and run the approved independent experiment pipeline.
- Files to read: project overview, experiment protocol, traceability map, configs.
- Files allowed to edit: entire independent repository.
- Required skills: experiment-results-planning, research-paper-sprint,
  paper-orchestration, verification.
- Evidence inputs: frozen generations, complete rankings, qrels loaded only after lock.
- Required artifacts: per-query Parquet/JSONL, aggregate CSV, figures, REPORT.md.
- Rejection checks: no mock values; no hidden fallback; no private dependency;
  no replay mismatch; no aggregate without source records.
- Validation: pytest, ruff, tiny run, hash verification, table regeneration.

