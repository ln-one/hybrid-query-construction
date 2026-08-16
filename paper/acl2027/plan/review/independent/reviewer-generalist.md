# Independent ACL Main Long-Paper Review (Generalist)

## Paper summary and claimed contributions

The paper argues that fixed top-$L$ hybrid fusion confounds two effects: the query construction being evaluated and the amount of each component ranking admitted to fusion. It therefore evaluates query constructions using complete-list weighted reciprocal-rank fusion (WRRF), then replays dense and sparse access until the ordered fused top-20 is certified. On top of this protocol, it proposes DESA, an asymmetric use of the same LLM-generated references: an orthogonal residual is added to the dense query representation, while sparse BM25 scores for the original and expanded queries are multiplied so that generated terms can reorder, but not admit, documents outside the original lexical support.

The claimed contributions are: (i) evidence that fixed-$L$ evaluation can change the measured ordering of expansion methods (Results, Table 1); (ii) the two-operator DESA construction (Section 3); (iii) a seven-benchmark controlled evaluation reporting quality gains and lower replay depths relative to no expansion (Results, Table 2); and (iv) robustness analyses over generators, encoders, reference counts, WRRF constants, and corpus scales (Sections 4.4 and 5.5).

## Strengths

1. **The problem decomposition is unusually clear.** The Introduction, especially paragraphs 2--4, cleanly separates the ranking produced by a query construction from the evidence depth required to certify that ranking. Section 3.4 then connects this distinction to an exact replay criterion. This is an intelligible and ACL-relevant way to study hybrid retrieval beyond a single arbitrary cutoff.

2. **DESA is simple, motivated, and internally coherent.** The orthogonal residual in Section 3.3 removes the component parallel to the original unit query before adding the remaining reference signal; the score product in Eq. (5) preserves original-query lexical support under a non-negative scorer. The dense/sparse asymmetry directly follows the motivating NFCorpus example in the Introduction rather than appearing as an ad hoc collection of modules.

3. **The controlled comparison isolates integration effects well.** Section 4.3 gives Shared expansion and DESA identical generated references, so their difference is attributable to the two channel operators. Table 2 reports a useful quality/depth trade-off: DESA has the best macro nDCG@10 and Recall@20, while Shared has the smallest macro replay depths. The NFCorpus result in Section 5.2 is a concrete case where unconstrained sparse expansion increases depth and anchoring reverses that behavior.

4. **The evaluation scope is broad in several important dimensions.** The main controlled experiment spans seven heterogeneous benchmarks (Section 4.2), and Section 5.5 reports a second generator, a second dense encoder, a nested-corpus analysis, and an explicit Touch\'e-2020 failure case. The paper does not present access reduction as universal.

5. **Reproducibility details are stronger than average.** The appendix specifies model revisions, decoding parameters, deterministic seed construction, the complete generation prompt, validation/fallback behavior, encoder details, BM25 settings, tie-breaking, replay bounds, and artifact hashes. Section A.6 is particularly good traceability practice.

## Acceptance-critical weaknesses

1. **The long-paper evidence is not sufficiently inspectable because almost all primary results are macro averages.** Table 2 contains only five macro rows; it does not provide per-dataset quality, depth, sparse-support size/exhaustion, confidence intervals, or query counts. Yet Section 4.5 says 95% bootstrap intervals are computed, Section 4.1 promises sparse support and exhaustion rates, and the abstract makes a query-level 63.31% claim. None of these are shown in a table. Section 5.2 selectively discusses NFCorpus, and Section 5.5 narrates ranges without presenting the underlying dataset-level values. A reader cannot determine whether the macro gains are consistent, driven by one or two datasets, or sensitive to the equal-dataset aggregation. This is especially important because the paper itself emphasizes a dataset-specific failure. For an empirical ACL long paper, the present evidence package feels incomplete.

2. **The central efficiency interpretation is only a logical replay result, not an end-to-end retrieval result.** Section 4.1 first constructs and fuses complete dense and sparse rankings; Section 3.4 then replays prefixes of those already materialized rankings. Section 4.5 correctly states that the measurement is logical replay depth rather than wall-clock latency, but the Introduction and Conclusion repeatedly frame the result as the amount of ranked evidence “required” or “accessed.” The paper does not implement an incremental retriever that realizes these savings, measure latency/compute, or account for LLM generation and the extra original/expanded sparse scoring pass in DESA. The certification-depth analysis is still meaningful, but the practical efficiency claim must either be demonstrated operationally or narrowed consistently to a ranking-concentration/certification property.

3. **The sparse “complete ranking” and zero-score semantics are underspecified in a way that affects both the target and replay depth.** Section 3.3 states that documents outside original-query support have anchored score zero and then says that sorting documents by this score produces $\pi_S$. Section 3.4 says missing ranks contribute zero, while the appendix says the replay bound becomes zero when a channel is exhausted. It is not explicit whether zero-score documents are excluded from $\pi_S$ (so that the list exhausts at the positive-score support) or included with identifier-based tie-breaking (so that every document has a sparse rank). These choices yield different complete-list WRRF targets and radically different stopping depths. The paper's sparse-support argument requires the former, but the formal definition reads like the latter. The definition, implementation, and exactness conditions should be made unambiguous.

4. **The paper currently overstates DESA's dominance over Shared expansion.** Table 2 shows that Shared is substantially shallower on both channels (607.4/606.7 versus DESA's 728.9/673.2), while DESA is better on quality. Section 5.2 reports that only the nDCG difference against Shared survives Holm correction; the significance/effect sizes for Recall and both depths against Shared are not reported. Thus the controlled result is a Pareto trade-off, not “better quality with less access” relative to the most relevant shared-evidence baseline. The Introduction's NFCorpus example establishes one failure mode of Shared, but the macro table favors Shared on depth. The main claim should explicitly state the comparison target for every improvement and report all four corrected tests against Shared.

5. **The prior-method comparison is not yet strong enough to establish main-conference novelty or impact.** On the common four-dataset subset, Query2doc slightly exceeds DESA in nDCG (.3461 versus .3446), while DESA's Recall advantage is also small (.5258 versus .5229; Table 3). The paper cites more recent and directly relevant integration approaches such as Word2Passage and Exp4Fuse in Section 2.2 but does not evaluate them or explain why a faithful comparison is infeasible. Moreover, Section A.3 omits MuGI's pseudo-relevance-feedback calibration, although Section 5.4 calls this a “full-method comparison.” These choices do not invalidate DESA, but they weaken the claim that the proposed construction advances the best available hybrid expansion methods. A main-paper case needs either stronger current baselines or a more carefully delimited novelty claim.

6. **The fixed-$L$ motivation is mathematically valid but empirically less consequential than the prose suggests.** The two highlighted reversals in Section 5.1 are only .0002 and .0007 nDCG (Table 1), with no uncertainty or significance analysis, and DESA remains the best method at every displayed cutoff. Exact top-20 disagreement is a useful diagnostic, but low exact-set/order agreement does not by itself show that standard evaluation conclusions materially change. The paper should quantify rank correlations, statistically meaningful method-order changes, and/or changes in accept/reject conclusions across $L$, rather than resting the motivation on numerically tiny swaps.

## Non-critical issues

1. **A dedicated limitations discussion is missing.** The Conclusion mentions the Contriever/Touch\'e failure and non-monotonic scaling, but should also cover English-only evaluation (Section 4.2), dependence on non-negative lexical scorers (Section 3.3), incomplete relevance judgments, generator cost and hallucination risk, the difference between replay depth and latency, and the lack of validation on learned sparse retrievers.

2. **Related work and experimental attribution are too thin for a long paper.** The bibliography has no citations for the benchmark suite/datasets, BM25, WRRF, Pyserini, BGE, Contriever, Qwen, or Mistral, despite their central role in Sections 3--4. This limits accessibility for general ACL readers and makes the paper look less complete than the experimental work itself.

3. **Several promised robustness results are not actually displayed.** Section 4.4 announces WRRF-constant, generated-only, binary-mask, reference-count, generator, encoder, and scale studies, but Results gives mostly narrative summaries and omits the WRRF-constant results entirely. These should appear in compact main/appendix tables with uncertainty.

4. **The aggregation over generation draws needs a more explicit definition.** Section 4.5 says the three runs are averaged within query, but it is unclear how discrete replay depths, “both depths decrease,” confidence intervals, and paired randomization are computed after this averaging. The 63.31% figure should be defined mathematically and accompanied by uncertainty.

5. **The paper would benefit from one concrete worked query.** A short example showing the five generated references, the residual effect, the support retained by sparse anchoring, and the resulting channel ranks would make the method accessible to readers outside IR and would help distinguish anchoring from ordinary concatenation.

## Strongest plausible rejection argument

The strongest rejection case is that the paper's main-conference story outruns the presented evidence: its main controlled result is only a macro table, its closest controlled baseline is actually shallower in both channels, its strongest prior baseline is essentially tied on quality, and its “access” gains are obtained by replaying precomputed complete rankings rather than by an implemented efficient retrieval system (Tables 2--3; Sections 3.4, 4.1, and 4.5). Combined with the ambiguous treatment of zero-score sparse documents, a reviewer cannot yet verify either the consistency of the empirical benefit or the operational meaning of the efficiency claim. The idea remains suitable for a stronger revision or possibly Findings, but the current manuscript does not yet make a complete ACL Main long-paper case.

## Changes most likely to raise the score by at least 0.5

1. Add full per-dataset tables for the primary and Shared comparisons, including nDCG@10, Recall@20, $L_D$, $L_S$, sparse-support/exhaustion, 95% CIs, query counts, and all four Holm-corrected tests. Include the per-dataset fraction of queries whose two depths decrease.
2. Resolve the zero-score/missing-rank definition formally and give pseudocode or a theorem statement specifying the exact replay target, exhaustion rule, and tie handling.
3. Either implement the incremental exact retrieval path and report end-to-end latency/compute (including generation and the extra sparse scoring), or consistently rename the outcome as certification/replay depth and remove operational efficiency implications.
4. Reframe Table 2 as a quality--depth Pareto comparison with Shared rather than a dominance claim. Add a compact trade-off analysis across datasets and, if possible, fusion weights.
5. Add at least one strong recent comparison directly addressing sparse/hybrid expansion (or provide a technically specific infeasibility argument), label the MuGI reproduction as an ablation without PRF, and report statistical uncertainty for Table 3.
6. Strengthen the fixed-$L$ study with uncertainty, method rank correlation across cutoffs, and the frequency/magnitude of practically meaningful reversals, then add a substantive Limitations section and the missing standard citations.

## Scores

- **Soundness:** 3/5. The core construction and evaluation logic are plausible, but sparse-rank semantics and the lack of disaggregated evidence prevent full verification.
- **Excitement:** 3/5. Channel-asymmetric expansion and exact certification depth are interesting, but the operators are modest and the advantage over the strongest baselines is not yet decisive.
- **Overall assessment:** 2.5/5 (between resubmit and Findings). The paper has a credible contribution and strong reproducibility intent, but needs a more complete empirical record and narrower or operationally validated access claims.
- **Reviewer confidence:** 4/5. I am confident in the generalist ACL assessment and in the internal argument/evidence gaps identified here; I am less certain how difficult it is to realize the replay savings in specific ANN/Lucene serving systems.

## Verdict

**resubmit**
