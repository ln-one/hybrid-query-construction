# Task packet: ACL readiness audit and low-risk evidence repair

## Scope

Audit the current ACL review PDF after the DESA overview figure was integrated,
then apply only revisions that reuse frozen artifacts and authoritative sources.
Do not regenerate retrieval or generation outputs.

## Evidence inputs

- `configs/datasets/formal-v1.yaml`
- `report/main-results.csv`
- `report/per-query-draw-mean.csv`
- `report/primary-paired-tests.csv`
- current anonymous PDF and LaTeX sources
- Kim et al. (2026), QuDAR, ACL Anthology ID `2026.acl-long.1791`

## Allowed changes

- label replay depth as policy-specific certification depth;
- make the finite Sparse support explicit;
- add QuDAR positioning without unsupported superiority language;
- expose per-dataset results in the appendix;
- keep the frozen seven-dataset primary results unchanged.

## Validation

- build anonymous and arXiv PDFs;
- check undefined citations/references and overfull boxes;
- render and inspect pages containing the new tables;
- run `git diff --check`.
