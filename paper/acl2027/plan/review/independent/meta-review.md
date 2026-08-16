# ACL Main Long-Paper Meta-Review

## Review setup

Three reviewers read the complete anonymous manuscript independently under the
current ACL Rolling Review rubric. Their assigned perspectives were: novelty
and conceptual contribution, IR methodology and statistics, and ACL
generalist assessment. They did not read one another's reports before
submitting them. Planned figures were explicitly excluded from this round and
their absence did not lower any score.

## Score summary

| Reviewer | Soundness | Excitement | Overall | Confidence | Verdict |
|---|---:|---:|---:|---:|---|
| Novelty / IR | 3.5 | 3.0 | 3.0 | 4.0 | Findings |
| Methods / statistics | 3.0 | 3.0 | 2.5 | 4.0 | Resubmit / borderline Findings |
| ACL generalist | 3.0 | 3.0 | 2.5 | 4.0 | Resubmit |
| **Meta-assessment** | **3.0** | **3.0** | **2.5--3.0** | **4.0** | **Not Main in the current form** |

Under the ARR scale, all reviewers regard the paper as interesting and
scientifically plausible. None recommends ACL Main in its current form. One
would accept it to Findings; two judge that substantial but tractable revision
is still needed.

## Consensus strengths

1. **The paper has a real and memorable core.** The separation between query
   construction, complete-fusion quality, and the rank evidence needed to
   certify that result is intellectually useful. The phrase “Dense Expands,
   Sparse Anchors” accurately communicates the proposed asymmetry.

2. **DESA is coherent rather than a bag of tricks.** The Dense residual and
   Sparse anchoring operators correspond to recognizable failure modes of
   semantic and lexical expansion. The NFCorpus case is a particularly useful
   demonstration of why shared expansion can deepen Sparse access and why
   anchoring can reverse it.

3. **The controlled comparison is a strong design choice.** Shared expansion
   and DESA use the same generated passages, so their comparison isolates the
   integration rule better than a comparison among unrelated prompts and
   generators. The $2\times2$ experiment is also an appropriate starting point
   for mechanism analysis.

4. **The empirical scope and disclosure are good.** Seven datasets, three
   generation draws, second-generator and second-encoder checks, reference
   count and scale studies, and the explicit Contriever/Touch\'e failure make
   the project more credible. Reviewers also valued the detailed revisions,
   seeds, parser behavior, tie-breaking, and artifact hashes in the appendix.

5. **The primary comparison with no expansion is credible.** The frozen paired
   analysis supports positive effects on nDCG@10, Recall@20, and both replay
   depths. The reviewers did not identify a fundamental error in the DESA
   construction or in the principal no-expansion effectiveness result.

## Acceptance-critical issues

### P0: submission and numerical correctness

1. **The anonymous manuscript has no dedicated Limitations section.** Current
   ARR guidance lists a missing Limitations section as a desk-rejection issue.
   The discussion currently scattered through Results and Conclusion is not an
   adequate submission-format substitute.

2. **The anonymous build uses `\usepackage[preprint]{acl}` rather than review
   mode.** The paper should be rebuilt with the current anonymous review style
   and checked again for length, line numbers, anonymity, and formatting.

3. **Two mechanism percentages conflict with the frozen results.** Section 5.3
   reports Dense-only access reductions of 8.85%/9.82% and Sparse-only
   reductions of 24.70%/24.17%. `report/access-macro-bootstrap.csv` gives
   8.16%/7.49% and 28.77%/27.74%, respectively. These differences are not
   rounding. All numerical prose and tables must be regenerated from a single
   frozen reporting path and audited before the paper can be submitted.

### P1: evidence required for a sound long paper

4. **The main evidence is too aggregated.** The manuscript promises
   per-dataset results and confidence intervals but primarily shows macro point
   estimates. A seven-benchmark claim needs a compact per-dataset record for
   quality, the two replay depths, support/exhaustion behavior, query counts,
   and paired uncertainty. Without this, readers cannot tell whether the macro
   effect is consistent or concentrated in a few collections.

5. **The Sparse candidate universe is formally ambiguous.** The paper must say
   whether zero-score BM25 documents are absent from the Sparse ranking or
   included as an identifier-tied tail. That choice changes the complete WRRF
   target, exhaustion behavior, and stopping depths. The intended semantics
   appear to be finite positive-score support, but the formal text must state
   this unambiguously and match the implementation.

6. **The replay depths are policy-specific, but some prose presents them as an
   intrinsic minimum.** The frozen procedure chooses the channel with the
   larger next WRRF upper bound. Under equal weights this tends to alternate
   channels, so the observed $(L_D,L_S)$ is a sufficient stopping pair produced
   by that schedule, not automatically a minimal or cost-optimal pair. The
   paper should either prove an objective for which the schedule is optimal,
   compute a minimal/Pareto certificate, or consistently call the measurements
   frozen-policy replay/certification depths and analyze schedule sensitivity.

7. **The development/evaluation boundary is unclear.** NFCorpus both motivates
   the method and appears in the seven-dataset primary result; the manuscript
   does not identify which data informed the prompt, five-reference choice,
   product operator, or other design decisions. “Held-out” should be defined
   precisely, or the primary analyses should be described as descriptive
   rather than confirmatory.

8. **The statistical record is incomplete.** The paper should show effect
   sizes, 95% intervals, raw and Holm-adjusted values for all declared primary
   outcomes, explain whether correction is over four or eight tests, and expose
   generation-run variability rather than only averaging runs within query.
   The Shared comparison is especially important: only nDCG is significant in
   the frozen paired table; Recall and both depth differences are not.

### P1: what currently prevents a Main recommendation

9. **The novelty map is too thin.** The manuscript must distinguish explicitly
   what is inherited from EAHR, what is newly introduced by DESA, and how the
   two operators differ from classic query-drift control, Rocchio/projection
   updates, lexical gating/rescoring, score combination, and recent
   channel-aware expansion. A simple method can be a Main contribution, but
   the current ten-reference positioning does not yet establish that case.

10. **The product and residual operators need stronger functional controls.**
    The binary mask shows that graded original-query scores matter, but not
    that score-product anchoring is the right way to use them. Reasonable
    controls include a support-masked additive or rank-level combination and a
    geometric/log-space alternative; Dense needs a direct interpolation or
    residual-weight control. These are the experiments most likely to separate
    a new principle from generic rescoring.

11. **The generation contribution is claimed but not isolated.** The paper
    attributes gains partly to complementary, intent-preserving reference
    generation, yet the controlled ablation only isolates the retrieval
    operators. Either add a prompt-level control at the same generation budget
    or narrow the contribution to the integration mechanism.

12. **The prior-method comparison is not yet decisive.** It uses only four
    datasets, Query2doc is essentially tied on quality, closer cited methods
    are absent, and MuGI omits its PRF calibration while the section is called
    a full-method comparison. The paper should separate faithful reproduction
    from common-generator/operator controls, explain the common subset, and
    add uncertainty or significance.

13. **Logical access must not be sold as measured system efficiency.** The
    replay is scientifically useful, but it is performed over materialized
    complete rankings and excludes generation, extra encoding/scoring, and an
    executable lazy index. Either demonstrate a realizable incremental
    retriever or frame the result throughout as certificate depth/ranking
    concentration rather than latency or end-to-end cost.

### P2: framing and completeness

14. **The fixed-Top-$L$ examples establish sensitivity, not yet material
    conclusion instability.** The two reported method-order reversals are only
    0.0002 and 0.0007 nDCG and have no uncertainty. Exact Top-20 disagreement is
    informative, but it does not by itself prove that evaluation conclusions
    change meaningfully. Add paired uncertainty, rank correlations, or the
    frequency and magnitude of practically relevant reversals; otherwise
    soften the “confound” claim and present complete-list evaluation as a
    complementary estimand.

15. **Shared expansion should be presented as a Pareto comparison.** At the
    seven-dataset macro level Shared is shallower, while DESA has higher quality;
    only the nDCG advantage is statistically clear. NFCorpus remains valuable
    as a failure case for Shared, but it should not be generalized into overall
    dominance.

16. **Standard experimental citations and missing promised results should be
    added.** The draft lacks standard references for BM25, WRRF, Pyserini,
    datasets, encoders, and generators, and announces a WRRF-constant analysis
    that does not appear in Results. Mean depth should be supplemented by
    medians/upper quantiles because its distribution is heavy-tailed.

## Reviewer disagreement and synthesis

The novelty reviewer is willing to recommend Findings now because the main
no-expansion result is credible and the idea is useful. The methods and
generalist reviewers prefer resubmission because the access metric's semantics,
statistical reporting, and disaggregated evidence are central rather than
cosmetic. This is not a disagreement about whether the idea is promising; it
is a disagreement about whether the current manuscript makes all of its main
claims inspectable.

The strongest shared rejection argument is therefore not “the method is only a
projection and a multiplication.” It is that the manuscript asks its bespoke
replay metric to carry a Main-level evaluation claim without yet proving what
the stopping pair means, while the operator novelty and empirical record are
not sufficiently separated from straightforward alternatives.

## Meta-verdict

**Current state: 2.5--3.0 overall, between resubmit and Findings; not ACL Main.**

The paper has a credible route upward. Fixing the Limitations/style/numerical
issues, exposing the seven-dataset evidence, formalizing Sparse and replay
semantics, and correcting the Shared/efficiency framing should make a solid
Findings submission. Reaching ACL Main likely also requires the stronger
operator controls, a precise novelty map, and a convincing demonstration that
the Top-$L$/certification perspective changes scientific conclusions or enables
a meaningful operational benefit.

This judgment does not count missing figures. Figures could improve clarity,
but they would not by themselves resolve any acceptance-critical issue above.
