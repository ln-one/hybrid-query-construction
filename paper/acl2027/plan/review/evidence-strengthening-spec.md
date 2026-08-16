## Evidence-strengthening specification review

- Scope remains one unified seven-dataset evaluation; no development or
  held-out partition was introduced.
- All new results derive from frozen generations and ranking stores. Primary
  raw result files were not overwritten.
- The fixed-cutoff analysis compares each method with Original at the same
  cutoff and under complete-list fusion, distinguishing any sign change from a
  strict reversal.
- Operator controls change one transformation at a time while holding the
  other channel at its original-query ranking.
- The QuDAR baseline follows the official rank-based QuDAR-simple design:
  OS/ES/OD/ED, Top-1000 per signal, and RRF constant 60. Confidence and LLM
  variants are explicitly out of scope because the frozen artifacts lack their
  required score or judgment inputs.
- Statistical tests average three draws within query before stratified paired
  inference and apply Holm correction across nDCG and Recall per comparison.

Verdict: the implementation and manuscript match the task packet without
expanding the experimental population or overstating baseline coverage.
