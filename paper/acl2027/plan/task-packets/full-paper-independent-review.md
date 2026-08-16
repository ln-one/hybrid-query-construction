# Task Packet: Independent ACL Main Long-Paper Review

## Scope

Perform a read-only, independent review of the current anonymous manuscript as
an ACL main-conference long-paper submission. Do not edit the manuscript and do
not inspect other reviewers' reports. Figures are intentionally out of scope in
this round: do not penalize the paper merely because planned figures are absent.

## Files to read

- `paper/acl2027/main.tex`
- `paper/acl2027/sections/01-introduction.tex`
- `paper/acl2027/sections/02-related-work.tex`
- `paper/acl2027/sections/03-method.tex`
- `paper/acl2027/sections/04-experiments.tex`
- `paper/acl2027/sections/05-results.tex`
- `paper/acl2027/sections/06-conclusion.tex`
- `paper/acl2027/sections/a-appendix.tex`
- `paper/acl2027/references.bib`
- frozen report CSVs only when needed to verify a numerical claim

## Review standard

Use the current ACL Rolling Review form:

- paper summary
- numbered strengths
- numbered weaknesses
- soundness score (1--5)
- excitement score (1--5)
- overall assessment: 5 award, 4 conference, 3 findings, 2 resubmit, 1 do not
  resubmit; half points allowed
- reviewer confidence (1--5)

Judge a long experimental paper on originality, ACL relevance, methodological
validity, breadth and depth of evidence, fair comparison, reproducibility,
clarity, limitations, and likely impact. Main-conference recommendations must
consider novelty and impact in addition to soundness and reproducibility.

## Required artifacts

Each reviewer writes exactly one report under `plan/review/independent/` and
does not modify any other file. The report must include:

1. concise summary and claimed contributions;
2. strengths grounded in exact manuscript sections or tables;
3. weaknesses separated into acceptance-critical and non-critical issues;
4. the strongest plausible rejection argument;
5. concrete changes that could raise the paper by at least 0.5 overall points;
6. soundness, excitement, overall-assessment, and confidence scores;
7. a one-line verdict: ACL Main / borderline Main / Findings / resubmit.

## Rejection checks

- Do not reject merely because the method is simple.
- Do not demand unrelated experiments whose absence does not affect the claims.
- Do not treat limitations as automatic weaknesses.
- Do flag unsupported causal language, unfair comparisons, hidden selection,
  incomplete baselines, evaluation leakage, or irreproducible details.
- Do not count planned figures as missing evidence in this round.

## Validation

- Confirm that every major criticism cites a section, equation, table, or exact
  manuscript claim.
- Confirm that the scores are consistent with the written review.
- Confirm that only the assigned review file changed.
