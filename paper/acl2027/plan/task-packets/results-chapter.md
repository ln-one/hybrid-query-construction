# Task packet: Results chapter

## Goal

Write Section 5 from frozen formal-run artifacts and integrate it into the ACL
draft.

## Required claims

- Fixed Top-$L$ changes scores, method ordering, and agreement with the
  complete-list target.
- The proposed construction improves macro nDCG@10 and Recall@20 and reduces
  both stopping depths relative to the original query.
- Sparse anchoring supplies most of the quality gain; the joint construction
  gives the best controlled quality-access result.
- Against Shared, nDCG improves significantly while Recall and access-depth
  differences do not survive the corrected primary tests.
- Against complete methods, the proposed construction dominates HyDE and MuGI;
  Query2doc has slightly higher nDCG but lower Recall and deeper access.
- The method transfers to Mistral. Contriever on Touch\'e is the explicit
  access-depth failure case.

## Evidence sources

- `report/fixed-top-l-results.csv`
- `report/main-results.csv`
- `report/primary-paired-tests.csv`
- `report/ablation-results.csv`
- `report/fidelity-results.csv`
- `report/reference-count-results.csv`
- `report/robustness-results.csv`
- `report/scale-results.csv`

## Constraints

- Do not infer wall-clock latency from stopping depth.
- Do not describe complete-list fusion as relevance ground truth.
- Do not call the replay depths globally minimal.
- Do not claim monotonic scale improvement.
- Preserve mixed and negative outcomes.
