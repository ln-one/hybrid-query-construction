# Figure and Table Literature Audit

## Stage and question

- Stage: S3 experiment/result design and S5 evidence review.
- Question: which main-text visuals materially advance DESA's argument, and
  which visual conventions from strong retrieval papers can be transferred to
  a one-column ACL layout?
- Boundary: this audit recommends changes but does not edit the manuscript or
  regenerate figures.

## What the reference papers do well

### QuDAR

- Each analysis subsection is organized as research question, experimental
  setting, figure, observation, and insight. The figure is therefore an answer
  to a named question rather than a decorative summary.
- The main analysis figures are predominantly one-column: paired weighting
  curves, a compact histogram-plus-bar composition, and paired heatmaps.
- Color encodes datasets or evidence categories consistently; stars and
  reference lines mark optima without adding large annotation blocks.
- The full-width framework figure is reserved for the one diagram whose
  parallel branches genuinely need the width.

### Weller et al.

- The central multi-dataset figure compresses the paper's main empirical law:
  base retriever strength is shown together with the distribution of expansion
  outcomes, so the negative relationship is visible before reading the table.
- Large tables retain detailed method-by-dataset values, while figures are used
  for relationships and failure mechanisms. The two formats have different
  jobs.

### MuGI

- Main tables are grouped by retriever family and evaluation domain. Ablation
  figures are used for parameter sensitivity and mechanism diagnostics rather
  than repeating the headline table.
- The paper is less suitable as a visual-style template: several dense tables
  are difficult to scan at page scale. Its useful lesson is evidence grouping,
  not visual density.

### Exp4Fuse

- The method figure makes the two retrieval routes and fusion stage explicit,
  but it relies on a full-width illustration. Its results are table-heavy.
- It is a useful negative template for the current constraint: a wide pipeline
  with large icons and long text labels should not be copied into a one-column
  DESA figure.

## Audit of the current main-text visuals

| Item | Claim-level role | Decision | Reason |
|---|---|---|---|
| Figure 1, retrieval examples | Dense can recover missing semantics; Sparse anchoring filters expansion-only matches | Keep | It explains the asymmetric intuition before formalism and is legible in one column. |
| Figure 2, DESA design | The same generated evidence enters the two channels through different operators | Keep | It is the shortest visual description of the method and now sits beside the method overview. Do not redraw it in this task. |
| Figure 3, fixed-$L$ judgment transitions | A fixed cutoff can change or strictly reverse the per-query assessment of expansion | Keep | The revised transition matrices directly encode the claim. The old cutoff curve showed convergence but did not make the decision reversal visually primary. |
| Table 1, controlled macro results | DESA improves retrieval quality and reduces certified access relative to Original | Keep, polish | It carries the headline values and the 2-by-2 construction controls. It is not interchangeable with a relationship figure. |
| Figure 4, angle and turnover distributions | The implemented operators stay within the Dense bound and alter Sparse ranking order | Move to appendix or replace in main text | It verifies internal behavior but does not show that the behavior produces useful outcomes. The prose must supply the outcome connection, so its main-text evidentiary return is limited. |
| Table 2, prior query-expansion methods | DESA is competitive in quality and requires less ranked evidence on the common subset | Keep, restructure | It is the correct format for exact comparisons, but the closest recent baseline, QuDAR-simple, currently appears only in prose and the appendix. |

## Highest-value new main-text figure

Replace the current main-text mechanism distribution with one single-column,
two-panel figure built only from frozen per-dataset results.

### Panel A: Dense expansion outcome

- Horizontal lollipop or point plot by dataset.
- Quantity: Dense-only change in nDCG@10 relative to Original.
- Zero reference line; blue points; preserve the small FiQA negative result.
- Supported claim: the Dense residual is beneficial on six of seven datasets,
  with one near-zero negative case rather than universal improvement.

### Panel B: Sparse support preservation

- Paired point plot by dataset for `Shared / Original` and `DESA / Original`
  Sparse-support size.
- Use a log-scaled x-axis, a reference line at 1, muted gray for Shared, and
  green for DESA.
- Frozen data show exact 1.00 support retention on six datasets and 99.9999\%
  retention on Touch\'e-2020, whereas Shared expansion ranges from 1.003 to
  5.72 times the original support.
- Supported claim: score-product anchoring preserves the original lexical
  support by construction while symmetric expansion can broaden it sharply.

This figure supports the title-level division of labor directly. It is not a
replacement for Table 1: the table answers how well the methods perform in the
macro comparison; the figure answers what each channel-specific operator does
across datasets.

## Table changes worth making

1. Standardize metric headers as `nDCG@10 $\uparrow$`, `Recall@20 $\uparrow$`,
   `$L_D \downarrow$`, and `$L_S \downarrow$`; use leading zeros consistently.
2. Retain bold best and underlined second-best values, matching QuDAR's compact
   table convention.
3. Bring the matched-evidence QuDAR-simple comparison into the main text as a
   clearly separated two-row block or subtable. Do not merge its seven-dataset
   macro values with the four-dataset prior-method block without an explicit
   subset header.
4. Keep full per-dataset numerical tables in the appendix. A new main-text
   table is justified only for the closest baseline comparison, not for another
   repetition of all seven datasets.

## Priority

1. P0: keep Figures 1--3 and Table 1; do not add a quality--access scatter.
2. P1: replace the main-text Figure 4 with the channel-specific outcome figure;
   move the unchanged angle/turnover distribution to the appendix.
3. P1: expose the matched QuDAR-simple comparison in a compact, explicitly
   labeled main-text table block.
4. P2: polish numerical formatting and metric-direction headers.
5. P3: add no further robustness figure unless a reviewer specifically asks;
   the current failure-boundary prose and appendix results are sufficient.

## Spec-compliance review

- Every recommendation maps to a named manuscript claim.
- No proposed figure duplicates the main macro table.
- All proposed inputs are frozen real data; no synthetic values are used.
- The recommended plot is designed for one-column width.
- The FiQA Dense-only negative, the ArguAna DESA-versus-Shared negative, and
  the 25 extremely low-scoring Touch\'e-2020 tail omissions are retained rather
  than hidden.

## Quality review

- The reference papers were used for argument structure and information
  allocation, not copied as ornamental styling.
- The strongest transferable QuDAR pattern is question-to-figure adjacency.
- The strongest transferable Weller pattern is a cross-dataset relationship
  that makes the central empirical law visible.
- Remaining risk: the proposed support plot establishes Sparse support
  preservation, not end-to-end latency or universally lower Sparse depth; its
  caption and prose must preserve that distinction.
