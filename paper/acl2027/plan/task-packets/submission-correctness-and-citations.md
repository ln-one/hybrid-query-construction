# Task Packet: Submission Correctness and Experimental Attribution

## Scope

Repair the current ACL/arXiv manuscript without changing the research claims:
use seven datasets as the default numerical scope, keep anonymous review and
public preprint builds separate, add the mandatory Limitations section, correct
the frozen seven-dataset mechanism percentages, and add standard experimental
citations.

## Files to read

- `main.tex`, `main-arxiv.tex`, `Makefile`
- `sections/03-method.tex`, `04-experiments.tex`, `05-results.tex`,
  `06-conclusion.tex`, and `a-appendix.tex`
- `references.bib`
- `report/access-macro-bootstrap.csv`
- current ARR reviewer guidelines and ACL style configuration

## Files allowed to edit

- the files above except frozen report CSVs
- new `sections/07-limitations.tex`
- planning, evidence, and review records under `paper/acl2027/plan/`

## Required skills

- paper orchestration
- evidence-driven writing and literature review
- LaTeX output
- verification

## Evidence inputs

- seven-dataset frozen reporting CSVs
- official papers/pages for BEIR and component datasets
- original BM25, RRF, Pyserini, BGE, Contriever, Qwen2.5, and Mistral papers

## Required artifacts

1. Anonymous `main.pdf` built in ACL review mode.
2. Public `main-arxiv.pdf` retained in preprint mode with author metadata.
3. Dedicated Limitations section shared by both builds.
4. Correct seven-dataset mechanism percentages in English and Chinese sources.
5. Verified BibTeX entries and citations in the experimental setup.

## Rejection checks

- Do not alter the arXiv author block or convert the arXiv build to review mode.
- Do not replace seven-dataset primary values with the older four-dataset
  subset. Four-dataset values may appear only when explicitly described as the
  common baseline/robustness subset.
- Do not invent bibliographic metadata.
- Do not claim online latency or end-to-end cost in Limitations.

## Validation commands

- rebuild both PDFs from clean state;
- check unresolved citations and references;
- inspect PDF text for author anonymity versus public authorship;
- check review/preprint mode markers and dedicated Limitations;
- compare every corrected percentage with the frozen CSV;
- run `git diff --check`.
