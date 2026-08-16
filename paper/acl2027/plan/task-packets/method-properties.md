# Task Packet: DESA Operator Properties

## Scope

Strengthen the Method section with concise, verifiable properties of the two
channel-specific operators. The main text should state only the properties that
explain the design; short derivations belong in the appendix.

## Files to read

- `sections/03-method.tex`
- `sections/a-appendix.tex`
- `src/hybrid_query_construction/methods.py`
- `src/hybrid_query_construction/retrieval.py`
- `tests/test_methods.py`
- `configs/retrievers/formal-v1.yaml`

## Files allowed to edit

- `sections/03-method.tex`
- `sections/a-appendix.tex`
- `tests/test_methods.py`
- `plan/progress.md`

## Required skills

- research-writing workflow
- paper orchestration
- method chapter writing
- LaTeX output
- verification

## Required properties

1. With unit-normalized contextual reference vectors, orthogonal residual
   expansion remains within 45 degrees of the original dense query and reduces
   to it when the residual vanishes.
2. With a non-negative additive sparse scorer and an expanded query containing
   the original query, score-product anchoring exactly preserves the original
   positive-score support.
3. If the expanded sparse score is a positive multiple of the original score,
   anchoring preserves the original ranking; positive global score rescaling
   also leaves the anchored ranking unchanged.

## Rejection checks

- Do not claim the angle bound without defining each contextual vector as unit
  normalized.
- Do not generalize sparse support preservation beyond non-negative additive
  scorers.
- Do not present elementary consequences as a large theoretical contribution.
- Keep the main-text addition short and consistent with the existing prose.
- Do not change frozen experimental artifacts or numerical results.

## Validation commands

- run the method unit tests;
- rebuild both the public preprint and anonymous review PDFs;
- check unresolved references, overfull boxes, and malformed math;
- inspect the rendered Method pages;
- run `git diff --check` on the edited files.
