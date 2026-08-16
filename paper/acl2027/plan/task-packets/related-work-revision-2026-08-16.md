## Task Packet

- Scope: revise the complete Related Work chapter after paragraph-level author
  review.
- Files to read: `sections/01-introduction.tex`,
  `sections/02-related-work.tex`, `sections/03-method.tex`,
  `plan/project-overview.md`, `plan/outline.md`, `plan/evidence-map.md`, and
  `plan/review/evidence-coverage.md`.
- Files allowed to edit: `sections/02-related-work.tex`, its Related Work
  blueprint, and the project progress record.
- Required skills: research-writing workflow, paper orchestration,
  evidence-driven writing, literature review, chapter writing, LaTeX output,
  and completion verification.
- Evidence inputs: the primary works already recorded in `references.bib`, with
  QuDAR positioning constrained by evidence item E28.
- Argument chain: generated evidence -> cutoff-conditioned hybrid evaluation
  -> channel-aware integration -> concise QuDAR/DESA boundary.
- Prohibited structure: paper-by-paper summaries, Method-level operator detail,
  repeated replay mechanics, and unsupported superiority claims.
- Required artifact: a concise three-subsection Related Work chapter using the
  ACL LaTeX citation style.
- Rejection checks: no duplicated Method exposition; no claim that DESA
  dominates QuDAR; no detailed replay description already given in the
  Introduction and Method.
- Validation commands: `make -C paper/acl2027 all`, log scan for unresolved
  citations/references and LaTeX errors, and `git diff --check`.

### Review record

- Spec review: the author approved the revised subsection order and the
  compressed QuDAR comparison before write-back.
- Quality review: each paragraph has one role, citations remain attached to
  their supported claim families, and the chapter does not restate DESA's
  equations or replay mechanics.
- Verification: the anonymous ACL build completed at 15 pages; citation and
  reference scans found no unresolved entries or LaTeX errors; rendered pages
  2--3 showed a clean Related Work--Method transition without overlap or
  clipping; `git diff --check` was included in the final scoped check.
