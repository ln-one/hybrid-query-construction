# Writing progress

## Current stage

Stage S2/S6: Method-property formalization within public preprint readiness. The public
preprint is the immediate release target; the anonymous ACL review build is
maintained from the same source but is not the current submission priority.

The Chinese Results chapter has been approved by the author and written back.
The English Results chapter has been rebuilt from that approved argument and
is ready for paragraph-level author review. The approved Chinese Conclusion
has been translated, reviewed, and added to the ACL draft. The abstract now
includes the frozen primary findings and observed access boundary.
The title and method name are locked as `Dense Expands, Sparse Anchors:
Channel-Asymmetric Query Expansion for Hybrid Retrieval` and DESA (Dense
Expansion and Sparse Anchoring).
The manuscript now has a shared-source public arXiv build with the author's
name, affiliation, location, and contact email; the ACL build remains anonymous.

## Status

- [x] Core terminology provisionally locked.
- [x] ACL review-format project initialized.
- [x] Introduction paragraph 1 translated and cited.
- [x] Introduction paragraph 1 approved by the author.
- [x] Introduction paragraphs 2--4 translated, reviewed, and cited.
- [x] Introduction closing paragraph translated and approved by the author.
- [x] Related Work Section 2.1 translated, reviewed, and cited.
- [x] Related Work Section 2.2 translated, reviewed, and cited.
- [x] Related Work Section 2.3 translated, reviewed, and cited.
- [x] Method Section 3.1 translated and reviewed.
- [x] Method Section 3.2 translated and reviewed.
- [x] Method Section 3.3.1 translated and reviewed.
- [x] Method Section 3.3.2 translated and reviewed.
- [x] Method Section 3.4 translated and reviewed.
- [x] Experiments opening and Section 4.1 translated and reviewed.
- [x] Experiments Section 4.2 translated and reviewed.
- [x] Experiments Section 4.3 translated and reviewed.
- [x] Experiments Section 4.4 translated and reviewed.
- [x] Experiments Section 4.5 translated and reviewed.
- [x] Reproducibility material checked against the frozen protocol and
  implementation, translated, and organized into Appendices A--C: generation
  and baselines, operator properties and diagnostics, and retrieval and access
  analysis.
- [x] Abstract problem statement, method summary, primary findings, and access
  boundary reviewed and added.
- [x] Results Section 5.1: fixed Top-$L$ sensitivity drafted from frozen data.
- [x] Results Section 5.2: primary quality and access findings drafted.
- [x] Results Section 5.3: mechanism analysis drafted.
- [x] Results Section 5.4: complete-method comparison drafted.
- [x] Results Section 5.5: robustness and failure boundary drafted.
- [x] Chinese Results chapter created for paragraph-level author review.
- [x] Chinese Results chapter approved by the author.
- [x] English Results chapter rebuilt from the approved Chinese text.
- [x] English Results terminology and internal-consistency self-review completed.
- [x] Chinese Conclusion drafted from the approved findings.
- [x] Chinese Conclusion approved by the author.
- [x] English Conclusion written from the approved Chinese text.
- [x] Seven datasets established as the default scope for controlled, mechanism,
  and cutoff analyses; four-dataset results are labeled as common subsets.
- [x] Anonymous ACL build switched to `review` mode without changing the public
  arXiv build from `preprint` mode.
- [x] Dedicated Limitations section added to both builds.
- [x] Seven-dataset mechanism percentages reconciled with the frozen reporting
  CSVs in the English and Chinese Results sources.
- [x] Dataset, metric, fusion, retriever, encoder, toolkit, and generator
  citations added from primary sources.
- [x] Both public and anonymous PDFs rebuilt and checked for resolved citations,
  identity separation, and layout.
- [x] Dense and Sparse channel operators formalized with concise main-text
  properties and appendix derivations: bounded Dense drift, exact Sparse
  support preservation, rank consistency, and scale invariance.
- [x] Seven-dataset post-hoc mechanism diagnostics completed from frozen
  generations and rankings: realized Dense angles, Sparse turnover and support,
  relevant-document rank movement, within-dataset bins, and descriptive
  correlations.
- [x] Mechanism diagnostics written back into the shared manuscript source.
  The realized-operator distribution is in the main Results section; the
  nonmonotonic quartile analysis and Touch\'e-2020 support-export audit are in
  the appendix. Both anonymous and public-author builds include the figures.

## Capability-use audit

- Skills: research-writing workflow, paper orchestration, evidence-driven
  writing, literature review, LaTeX output, and completion verification.
- Evidence: frozen seven-dataset reporting CSVs; primary proceedings, journal,
  arXiv, and OpenReview records enumerated in `plan/evidence-map.md`.
- Artifacts: separate public and anonymous build entry points, a dedicated
  Limitations section, an expanded `references.bib`, and submission-correctness
  records under `plan/`.
- Scope audit: the manuscript uses seven datasets by default. The two remaining
  four-dataset analyses are explicitly the common prior-method subset and the
  sampled Mistral/Contriever robustness subset.
- Numerical audit: mechanism access reductions now match
  `report/access-macro-bootstrap.csv`: Dense-only 8.16\%/7.49\%, Sparse-only
  28.77\%/27.74\%, and DESA 36.90\%/36.56\% for Dense/Sparse.
- Method-property verification: the Dense bound was checked against normalized
  production embeddings, and dedicated tests cover the $45^\circ$ angle bound,
  Sparse support preservation, and the no-new-evidence ranking case. All nine
  original method tests pass; the mechanism diagnostics add two further passing
  tests for a known Dense angle and Sparse relevant-rank movement.
- Mechanism audit: all 11,327 query--draw rows satisfy the Dense angle bound.
  Sparse support is exact on six datasets; Touch\'e-2020 contains 25 missing
  tail-document occurrences across 23 query--draw cells, while mean support
  retention remains above 99.9998\%. This implementation boundary is retained
  in the mechanism artifacts rather than hidden.
- Build verification: `make arxiv` produced the signed public preprint and
  `make` produced the anonymous line-numbered review PDF. After the mechanism
  write-back, both builds are thirteen pages including references and appendix;
  the paper body ends before the ACL long-paper limit. The Results and appendix
  figure pages were rendered and inspected.
- Identity verification: the public PDF contains the author's name,
  affiliation, and email; the review title block is anonymous. The review
  bibliography retains ordinary third-person citations, including the related
  preprint.
- Remaining work before public release: decide whether the other planned result
  figures are still needed, perform a final prose/cross-reference pass, and
  package the arXiv source bundle. Further ACL review revisions are deliberately
  deferred until after the preprint release.

### Capability-use audit: mechanism diagnostics write-back

- Required skills: paper orchestration, experiment/results planning, chapter
  writing, core academic writing, English humanization, paper figures, LaTeX,
  PDF inspection, and verification.
- Skills actually used: all required skills above.
- Inputs consumed: frozen per-draw and per-query mechanism CSVs, summary and
  correlation CSVs, figure data files, mechanism manifest, current Experiments,
  Results, Appendix, and approved Chinese Results chapter.
- Inputs not used: no new generations, retrieval runs, citations, or primary
  significance tests were needed because this is a diagnostic write-back.
- Artifacts produced: one main-text PDF figure, one appendix PDF figure,
  revised English and Chinese Results text, revised experiment protocol text,
  an appendix diagnostic table and audit paragraph, and this task packet.
- Verification run: figure regeneration, anonymous and public LaTeX builds,
  visual inspection of Results and Appendix pages, full repository tests,
  linter, artifact-hash verification, identity checks, and `git diff --check`.
- Remaining risk: correlations are descriptive and must not be promoted to
  causal or confirmatory evidence; the Touch\'e-2020 full-ranking export is not
  exactly support preserving in 23 query--draw cells.

### Capability-use audit: ACL-readiness pass, 2026-08-15

- Skills used: research-writing workflow, paper orchestration, peer review,
  evidence-driven writing, LaTeX output, PDF inspection, and verification.
- Evidence used: the frozen seven-dataset reporting CSVs, the current ACL
  manuscript, and the official ACL Anthology record for QuDAR.
- Artifacts produced: direct QuDAR positioning, explicit finite-Sparse-support
  and policy-specific replay semantics, a seven-dataset per-collection table,
  and the complete seven-dataset primary statistical record.
- Scope decision: all seven collections remain one unified primary evaluation;
  no development/held-out split is asserted in the manuscript.
- Verification: anonymous and public PDFs compile to 14 pages with resolved
  citations and cross-references and no overfull boxes. The remaining warnings
  are underfull spacing warnings.
- Remaining evidence risks: no direct QuDAR experimental baseline is yet
  reported, operator-level functional controls remain limited, and the observed
  fixed-cutoff reversals are small in magnitude.

### Capability-use audit: evidence strengthening, 2026-08-16

- Skills used: research-writing workflow, paper orchestration,
  experiment/results planning, LaTeX output, PDF inspection, and completion
  verification.
- Evidence used: frozen seven-dataset complete and fixed-cutoff result records;
  frozen Dense/Sparse ranking stores; the ACL Anthology QuDAR paper; and the
  official QuDAR implementation at commit
  `0702721e82799d0489850d3f94ac787da43436ad`.
- Artifacts produced: query-level fixed-cutoff diagnostics, two matched
  operator-control comparisons, a matched-evidence QuDAR-simple RRF baseline,
  derived JSONL records and hash manifest, concise main-text findings, and
  three appendix tables.
- Scope audit: all new analyses use the same unified seven datasets. No
  development/held-out split was introduced.
- Statistical audit: the operator and QuDAR paired tests average the three
  draws within query, use equal-dataset stratified bootstrap/sign-flip
  inference, and apply Holm correction across nDCG and Recall per comparison.
- Claim audit: fixed-$L$ motivation is now supported by query-level conclusion
  changes; neither operator is claimed independently dominant; DESA is
  described as statistically comparable to QuDAR-simple, with 64.95% lower
  fusion-side rank-entry access rather than lower end-to-end latency.
- Verification: evidence reports were regenerated twice with stable artifact
  hashes; 53 tests passed; Ruff passed for `src`, `scripts`, and `tests`;
  `git diff --check` passed; both anonymous and public LaTeX builds completed
  at 15 pages with no undefined references or overfull boxes. Pages 7--9 and
  13--15 were rendered and visually inspected for legibility and float layout.
- Remaining risk: the direct recent baseline covers QuDAR-simple RRF only.
  QuDAR-confidence needs normalized scores absent from the frozen artifacts,
  and QuDAR-llm would require new relevance judgments.

### Capability-use audit: Related Work revision, 2026-08-16

- Stage: S1 evidence synthesis and S4 chapter revision.
- Required skills: research-writing workflow, paper orchestration,
  evidence-driven writing, literature review, chapter writing, LaTeX output,
  and completion verification.
- Skills actually used: all required skills; subagent delegation was omitted
  because the active workspace instructions prohibit delegation unless the
  user explicitly requests it.
- Inputs consumed: the approved bilingual revision, current Introduction,
  Related Work, Method, project outline, evidence map, evidence-coverage audit,
  QuDAR blueprint, and verified BibTeX records.
- Inputs not used: no new literature search or experimental artifact was needed
  because the revision introduced no new source or empirical claim.
- Artifacts produced: revised `sections/02-related-work.tex`, an expanded
  paragraph blueprint, and the persistent task packet for this revision.
- Verification run: the anonymous ACL build completed at 15 pages; no LaTeX
  errors or unresolved citations/references were reported; Related Work pages
  2--3 were rendered and visually checked; whitespace and scoped Git checks
  passed before commit.
- Remaining risk: the compact section positions the main recent integration
  methods but does not attempt a comprehensive history of classical query
  expansion.

### Method chapter review, 2026-08-16

- Stage: S2 Method and S4 chapter revision.
- Status: complete bilingual review draft prepared for paragraph-level author
  annotation; no manuscript write-back has been performed.
- Required skills: research-writing workflow, paper orchestration, chapter
  writing, and core academic writing.
- Skills actually used: all required skills; subagent delegation was omitted
  because the active workspace instructions prohibit delegation unless the
  user explicitly requests it.
- Inputs consumed: current Method and operator appendix, frozen implementation
  and method tests, retrieval and fusion code, generator prompt, project
  overview, outline, and chapter architecture.
- Artifact produced: `plan/task-packets/method-chapter-review-2026-08-16.md`
  and the bilingual review draft presented to the author.
- Verification run: input-to-output trace checked against the implementation;
  LaTeX and rendered-page verification remain pending author-approved
  write-back.
- Remaining risk: the access depths are policy-specific certificates rather
  than minimal depth or end-to-end latency, and this boundary must remain in
  the final text.

### Capability-use audit: Method revision write-back, 2026-08-16

- Stage: S2 Method, S4 chapter revision, and S5 verification.
- Required skills: research-writing workflow, paper orchestration, chapter
  writing, core academic writing, LaTeX output, PDF inspection, and completion
  verification.
- Skills actually used: all required skills; no subagent was used because this
  was a single author-approved chapter revision rather than a full-paper
  redraft.
- Inputs consumed: the approved bilingual Method draft, current DESA figure,
  implementation trace, method tests, project overview, outline, and task
  packet.
- Artifact produced: revised `sections/03-method.tex`.
- Verification run: anonymous and public LaTeX builds completed at 15 pages;
  neither log contains unresolved citations, unresolved references, LaTeX
  errors, or overfull boxes. All 11 method tests passed. Pages 2--4 of the
  anonymous build were rendered and checked for equation fit, figure placement,
  column flow, and section transitions. Scoped whitespace and Git checks were
  run before commit.
- Layout follow-up: Figure 2 was restored to the top of the left column on
  page 3. Removing the forced column break keeps the Dense derivation
  continuous and lets the two-column text flow naturally.
- Remaining risk: replay depth remains a policy-specific certificate; its
  interpretation is retained in the experiment protocol and limitations rather
  than repeated defensively in the Method chapter.

### Capability-use audit: Experiments revision write-back, 2026-08-16

- Stage: S3 Experiments, S4 chapter revision, and S5 verification.
- Status: the author-approved Section 4 revision has been written back to the
  manuscript.
- Required skills: research-writing workflow, paper orchestration, experiment
  planning, chapter writing, core academic writing, humanization, LaTeX output,
  and completion verification.
- Skills actually used: all required skills; no subagent was used because the
  workspace instructions prohibit delegation unless the author requests it.
- Inputs consumed: the current Experiments and Results sections, experiment
  protocol, method--experiment traceability record, table schema, fixed-Top-$L$
  diagnostics, baseline configurations, and the author's paragraph-level
  annotations.
- Artifacts produced: revised `sections/04-experiments.tex` with a clearer
  gain/tie/loss cutoff diagnostic, concise baseline descriptions, matched
  operator controls, and a compact statistical protocol.
- Verification run: anonymous and public LaTeX builds completed at 14 pages;
  neither log contains unresolved citations or references, LaTeX errors, or
  overfull boxes. Pages 4--5 were rendered and visually checked for column
  flow, spacing, and the transition into Results. Scoped whitespace checks
  passed.
- Remaining risk: Section 5.1 still uses the older phrase "changes the sign of
  the paired conclusion." It should be aligned with the clearer gain/tie/loss
  terminology when the Results section is revised.

### Results chapter review draft, 2026-08-16

- Stage: S3 Results and S4 chapter revision.
- Status: a complete bilingual review draft has been prepared for author
  annotation; `sections/05-results.tex` has not yet been changed.
- Required skills: research-writing workflow, paper orchestration, experiment
  results planning, chapter writing, core academic writing, humanization,
  LaTeX output, and verification.
- Skills actually used: all required skills; no subagent was used because the
  workspace instructions prohibit delegation unless the author requests it.
- Inputs consumed: the frozen fixed-cutoff diagnostics, main and bootstrap
  results, paired tests, access-change summaries, operator controls, mechanism
  diagnostics, reference-count study, prior-method comparison, QuDAR results,
  robustness matrix, scale results, chapter outline, traceability matrix, and
  the existing Results text.
- Artifact produced: a bilingual Section 5 revision for paragraph-level author
  review. No manuscript write-back has been performed.
- Verification run: all numerical statements in the proposed revision were
  recalculated or checked against the frozen CSV artifacts. In particular,
  gain/tie/loss changes and strict reversals were checked separately, and the
  access-reduction aggregation was distinguished from ratios of raw macro
  depths.
- Remaining risk: Table 2 should state that raw depths are macro means whereas
  the reported 36.90\% and 36.56\% reductions average within-dataset percentage
  changes. The final write-back must preserve the nonsignificant Recall and
  depth comparisons against Shared expansion and the Contriever failure on
  Touch\'e-2020.
- Author-review update: the second bilingual draft removes defensive phrasing,
  centers the joint effect of the two channel operators, and moves binary-mask,
  reference-count, detailed generator, encoder, and corpus-scale results to the
  appendix. The main text retains one concise robustness paragraph and the
  Contriever failure boundary.

### Results figure claim alignment and layout revision, 2026-08-16

- Replaced the cutoff trend plot with a single-column judgment-transition
  matrix at $L=50$. Its diagonal shows preserved gain/tie/loss judgments,
  off-diagonal cells show changed judgments, and the two highlighted corner
  cells show strict gain--loss reversals.
- Rewrote Section 5.1 so the figure answers one explicit question---whether a
  fixed cutoff changes the query-level gain/tie/loss judgment---and moved the
  complete macro curves and Top-20 agreement details to the appendix.
- Removed the quality--access scatter plot from the manuscript because it
  repeated the effectiveness and access-depth comparison already reported in
  Table 1.
- Kept Figure 3 and the main results table in source order within the column;
  the final layout places the figure after its evidence paragraph and Table 1
  after the Section 5.2 result statement.
- Regenerated the PDF/SVG/PNG figure, rebuilt the anonymous paper at 14 pages,
  and visually checked pages 5--7 for column flow, legibility, and float order.
