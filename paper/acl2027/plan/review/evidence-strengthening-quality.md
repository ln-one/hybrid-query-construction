## Evidence-strengthening quality review

- Fixed-$L$ motivation now rests on query-level conclusion-change rates, not
  only small macro method crossings.
- Functional controls show that neither proposed transformation independently
  dominates its matched control. The paper reports this negative result and
  reserves confirmatory language for the significant joint nDCG comparison.
- DESA and matched-evidence QuDAR-simple are statistically comparable on both
  metrics after Holm correction. The paper does not claim superiority.
- The 64.95% reduction is labeled fusion-side rank-entry access, not latency or
  total system cost.
- Detailed evidence is auditable in appendix tables and derived CSV/JSONL
  artifacts; the main Results section contains only the decision-relevant
  findings.

Remaining risk: the direct QuDAR comparison covers only its rank-based simple
variant, and the fixed-cutoff conclusion-change rates are descriptive rather
than a family of hypothesis tests. Both limitations are explicit.
