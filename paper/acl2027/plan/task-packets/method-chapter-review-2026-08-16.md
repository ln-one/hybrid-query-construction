## Task Packet

- Scope: revise the complete DESA Method chapter for paragraph-level author
  review before any manuscript write-back.
- Target chapter: `sections/03-method.tex`.
- Files to read: the current Method, Introduction, Related Work, operator
  appendix, implementation in `src/hybrid_query_construction/methods.py`,
  method tests, retrieval configuration, project outline, and chapter
  architecture.
- Files allowed to edit in this review round: this task packet and the project
  progress record. The manuscript remains unchanged until author approval.
- Required skills: research-writing workflow, paper orchestration, chapter
  writing, and core academic writing.
- Technical inputs: frozen DESA implementation, verified operator properties,
  current framework figure, and fixed evaluation semantics.
- Argument chain: original query -> complementary references -> Dense residual
  ranking and Sparse anchored ranking -> fixed fusion target -> channel access
  measurement.
- Required artifact: a complete bilingual Method draft suitable for
  paragraph-level annotation.
- Prohibited structure: module-list prose, repeated Introduction motivation,
  equations that do not define an operator or establish a necessary property,
  and any claim that replay depth is minimal, cost-optimal, or end-to-end
  latency.
- Rejection checks: the English and Chinese versions must describe the same
  input-to-output procedure; dense vectors must be unit normalized for the
  angle bound; sparse support preservation must remain conditioned on a
  non-negative additive scorer and complete score export; the replay policy
  must remain fixed and policy-specific.
- Validation before write-back: author approval, implementation traceability,
  LaTeX build, rendered-page inspection, method tests, and scoped Git diff.

### Review status

- Stage: S2 Method and S4 chapter revision.
- Current state: author-approved revision written back and verified.
