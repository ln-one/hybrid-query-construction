## Task Packet

- Scope: implement the author-approved main-text figure and table revision from
  the literature audit.
- Files to read: the audit artifact, `sections/05-results.tex`,
  `sections/a-appendix.tex`, `report/main-results.csv`, figure style helpers,
  table schema, and figure data manifest.
- Files allowed to edit: one new figure script and its generated artifacts,
  the figure data snapshot and manifest, `sections/05-results.tex`,
  `sections/a-appendix.tex`, the table schema, and `plan/progress.md`.
- Required skills: experiment-results planning, figures-python, LaTeX output,
  PDF inspection, and verification.
- Evidence/data inputs: frozen controlled results in
  `report/main-results.csv` and the existing matched QuDAR and prior-method
  aggregates.
- Required artifacts: a one-column two-panel channel-outcome figure in
  PNG/SVG/PDF, an explicit data snapshot, revised main-text placement, the
  unchanged old mechanism distribution moved to the appendix, and a compact
  grouped external-comparison table.
- Rejection checks: no synthetic data; preserve the FiQA negative Dense-only
  result and Touch\'e-2020 support-export caveat; do not mix seven-dataset and
  four-dataset macro values without visible group headers; do not claim access
  depth as latency.
- Validation commands: regenerate the figure; compare the data snapshot with
  the source CSV; run tests; compile anonymous and public PDFs; check LaTeX
  logs; render and inspect all affected pages; run scoped whitespace checks.
