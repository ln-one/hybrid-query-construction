# Task packet: Chinese Conclusion draft

## Owned file

`paper/acl2027/chapters/06_conclusion_zh.md`

## Role in the manuscript

Close the paper by returning to the cutoff-dependent evaluation problem,
summarizing the channel-asymmetric method and its principal seven-dataset
finding, and stating the observed boundary without adding a new discussion
section.

## Required sources

- `paper/acl2027/plan/outline.md`
- `paper/acl2027/plan/terminology.md`
- `paper/acl2027/chapters/05_results_zh.md`
- `paper/acl2027/sections/01-introduction.tex`
- `paper/acl2027/sections/03-method.tex`
- `paper/acl2027/sections/05-results.tex`

## Argument chain

1. Fixed top-$L$ can change the measured gain and relative ordering of query
   expansion methods, motivating complete-list effectiveness plus per-channel
   replay stopping depth.
2. The proposed channel-asymmetric construction uses complementary reference
   passages through orthogonal residual expansion for Dense and score-product
   anchoring for Sparse.
3. On seven evaluation datasets, it improves nDCG@10 and Recall@20 by 3.82%
   and 2.38% over no expansion, while reducing Dense and Sparse access depth by
   36.90% and 36.56%; 63.31% of queries become shallower in both channels.
4. The access benefit is not universal: the Contriever/Touché-2020 setting is
   a recorded failure case, and scale effects are non-monotonic.
5. Close with the implication that query expansion in hybrid retrieval should
   be designed and evaluated per channel, jointly considering retrieval
   effectiveness and access depth.

## Length and style

- Chinese first draft: 350--550 Chinese characters, preferably two paragraphs.
- No citations, bullets, subsection headings, table references, or new claims.
- Do not repeat every baseline comparison or robustness number.
- Do not claim theoretical minimum depth, online latency reduction, universal
  improvement, or dependence on EAHR execution.
- Use the locked terminology and natural Chinese prose; avoid defensive
  qualifications and promotional language.

## Required return

- Status: DONE, DONE_WITH_CONCERNS, NEEDS_CONTEXT, or BLOCKED.
- Changed file path.
- Argument chain summary.
- Unresolved gaps.
- Self-review against scope, terminology, evidence, and style constraints.
