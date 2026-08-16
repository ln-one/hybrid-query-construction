## Task Packet

- Scope: audit the manuscript's main-text figures and tables against strong
  retrieval and query-expansion papers, with priority on claim alignment and
  single-column presentation.
- Files to read: `sections/01-introduction.tex`, `sections/03-method.tex`,
  `sections/05-results.tex`, `sections/a-appendix.tex`, the current rendered
  PDF, `plan/evidence-map.md`, `plan/review/method-experiment-traceability.md`,
  `tables/table-schema.md`, `figures/data-manifest.md`, and frozen result CSVs.
- Reference papers: QuDAR (ACL 2026), Weller et al. (Findings EACL 2024),
  MuGI (Findings EMNLP 2024), and Exp4Fuse (Findings ACL 2025), using official
  ACL Anthology PDFs.
- Files allowed to edit: this task packet, the corresponding review artifact,
  and `plan/progress.md`. No manuscript or figure asset may be changed in this
  audit.
- Required skills: research-writing workflow, paper orchestration,
  experiment-results planning, PDF inspection, and peer review.
- Evidence/data inputs: `report/main-results.csv`,
  `report/access-changes-vs-original.csv`, `report/mechanism-summary.csv`, and
  the current figure scripts and rendered PDF.
- Required artifact:
  `plan/review/figure-table-literature-audit-2026-08-16.md`.
- Rejection checks: reject any proposed figure that merely duplicates a main
  table, lacks a one-sentence claim, depends on synthetic data, hides a known
  failure case, or cannot remain legible at one-column width.
- Validation commands: extract all figure/table references with `rg`, inspect
  official reference PDFs and the current rendered pages, and recompute any
  cited cross-dataset pattern from the frozen CSV files.
