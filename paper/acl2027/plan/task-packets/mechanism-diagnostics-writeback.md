# Task packet: Mechanism diagnostics write-back

## Scope

Integrate the completed seven-dataset mechanism diagnostics into the Experiments,
Results, and Appendix sections without changing the frozen primary claims.

## Files to read

- `report/MECHANISM.md`
- `report/mechanism-summary.csv`
- `report/mechanism-correlations.csv`
- `figures/data/mechanism-distributions.csv`
- `figures/data/mechanism-binned-effects.csv`
- `paper/acl2027/sections/04-experiments.tex`
- `paper/acl2027/sections/05-results.tex`
- `paper/acl2027/sections/a-appendix.tex`

## Files allowed to edit

- `paper/acl2027/main.tex`
- `paper/acl2027/Makefile`
- `paper/acl2027/sections/04-experiments.tex`
- `paper/acl2027/sections/05-results.tex`
- `paper/acl2027/sections/a-appendix.tex`
- `paper/acl2027/chapters/05_results_zh.md`
- `paper/acl2027/plan/progress.md`
- `figures/mechanism/*.py`
- figure and planning manifests

## Required skills

- `paper-orchestration`
- `experiment-results-planning`
- `writing-chapters`
- `writing-core`
- `humanizer`
- `figures-python`
- `latex-output`
- `verification`

## Required argument chain

The main text first reports the isolated operator outcomes, then checks whether
the realized rankings exhibit the intended channel behavior. Dense drift must be
reported as bounded and empirically modest. Sparse behavior must distinguish
useful relevant-document movement from undirected turnover. Nonmonotonic bins and
the Touché-2020 support-export exception belong in the appendix.

## Rejection checks

- Do not call descriptive correlations confirmatory or causal.
- Do not introduce an adaptive threshold or a new hyperparameter.
- Do not hide the Touché-2020 tail-support exception.
- Do not imply that an operator's magnitude monotonically predicts quality or depth.
- Do not repeat the entire primary-results table in prose.

## Validation

- Regenerate PNG, SVG, and manuscript PDF figures from the registered CSV files.
- Build both anonymous and public-author PDFs.
- Check citations, references, overfull boxes, manuscript identity, and figure paths.
- Run the repository tests, linter, mechanism hash audit, and `git diff --check`.
