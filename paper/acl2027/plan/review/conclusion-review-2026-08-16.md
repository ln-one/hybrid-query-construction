# Section 6 conclusion review

## Diagnosis

The current conclusion is factually consistent, but it largely repeats the
abstract in the same order: cutoff problem, evaluation protocol, DESA
construction, headline gains, and failure case. It does not retain two findings
that became central in the Results section: Sparse anchoring supplies the more
consistent effectiveness gain, while Dense residual expansion adds
complementary gains and reduces required ranked evidence; and DESA matches the
reconstructable QuDAR-simple RRF comparison in retrieval quality while using
64.95% fewer fusion-side rank entries. The revised conclusion should synthesize
these findings while preserving the distinction between logical replay depth
and end-to-end latency.

## Candidate revision

A fixed top-$L$ cutoff does not merely limit how much of each ranking is read
in hybrid retrieval; it also changes which cross-channel contributions enter
fusion and can alter the measured effect of query expansion. We separate
retrieval effectiveness from ranking access by evaluating the complete-list
fused result and replaying each channel until its ordered top-$K$ is certified.
Within this setting, DESA integrates generated evidence according to the
matching mechanism of each channel: orthogonal residual expansion adds
complementary semantic directions to Dense retrieval, while score-product
anchoring uses the same evidence to reorder documents within the original
Sparse support.

Across seven BEIR datasets, DESA improves equal-dataset macro nDCG@10 and
Recall@20 over Original by 3.82\% and 2.38\%, while reducing Dense and Sparse
replay depths by 36.90\% and 36.56\%. Sparse anchoring supplies the more
consistent effectiveness gain, whereas Dense residual expansion provides
complementary gains and further reduces the ranked evidence required to certify
the fused result. Under matched generated evidence, DESA is statistically
indistinguishable from QuDAR-simple RRF in retrieval quality while using 64.95\%
fewer fusion-side rank entries. These findings support channel-specific rather
than shared query expansion and show why retrieval quality should be reported
together with logical access depth. The access reductions are not universal:
depths increase with Contriever on Touch\'e-2020, and replay depth should not be
interpreted as end-to-end latency without an incremental retrieval
implementation.

## Narrative revision after author annotation

The previous candidate remained too close to an audit: it opened with the
evaluation caveat, enumerated safeguards, and ended by defending replay depth.
The stronger narrative starts from the paper's scientific finding, presents
the evaluation protocol only as the means used to expose it, and closes on the
channel-asymmetric design principle. Detailed failure and latency qualifications
remain in the following Limitations section.

Our results show that generated evidence plays different roles in the two
channels of a hybrid retriever. DESA reflects this asymmetry directly:
orthogonal residual expansion adds complementary semantic directions to the
Dense query, while score-product anchoring uses the same evidence to reorder
documents already supported by the original Sparse query. Complete-list fusion
and per-channel replay then separate the quality of the fused ranking from the
amount of ranked evidence needed to determine it, without conditioning the
result on a fixed top-$L$ cutoff.

Across seven BEIR datasets, DESA improves equal-dataset macro nDCG@10 and
Recall@20 over Original by 3.82\% and 2.38\%, while reducing Dense and Sparse
replay depths by 36.90\% and 36.56\%. Sparse anchoring provides the more
consistent effectiveness gain; Dense residual expansion adds complementary
improvements and further reduces the ranked evidence required for fusion. In
the matched comparison, DESA achieves retrieval quality comparable to
QuDAR-simple RRF while using 64.95\% fewer fusion-side rank entries. These
results support channel asymmetry as a practical design principle for query
expansion in hybrid retrieval. Generated evidence should broaden semantic
coverage in Dense retrieval while remaining tied to the original lexical
support in Sparse retrieval. Dense expands; Sparse anchors.

## Full bilingual candidate after closing-line review

The standalone slogan was too abrupt. The complete revision now uses a short
third paragraph to derive the title-level formulation from the cross-channel
evidence.

### English

This work shows that query expansion in hybrid retrieval should account for
the distinct matching behavior of Dense and Sparse channels. DESA implements
this channel-asymmetric view using a shared set of generated reference
passages. Orthogonal residual expansion adds complementary semantic directions
to the Dense query, whereas score-product anchoring uses the same evidence to
reorder documents within the original Sparse support. To evaluate this design
without tying its measured effect to a fixed top-$L$ cutoff, we determine the
fused ranking from complete channel lists and record the per-channel replay
depths needed to certify its ordered top-$K$.

Across seven BEIR datasets, DESA improves equal-dataset macro nDCG@10 and
Recall@20 over Original by 3.82\% and 2.38\%, while reducing Dense and Sparse
replay depths by 36.90\% and 36.56\%. The operator analysis clarifies the source
of these gains: Sparse anchoring provides the more consistent effectiveness
improvement, and Dense residual expansion contributes additional gains while
reducing the ranked evidence required for fusion. Under matched generated
evidence, DESA reaches retrieval quality comparable to QuDAR-simple RRF with
64.95\% fewer fusion-side rank entries.

Together, these findings point to a division of labor for query expansion in
hybrid retrieval. Generated evidence broadens semantic coverage in Dense
retrieval and, when anchored to the original query, improves ordering in Sparse
retrieval without broadening lexical support. This division of labor captures
the central design principle of DESA: Dense expands, while Sparse anchors.

### Chinese translation

本研究表明，混合检索中的查询扩展需要考虑 Dense 与 Sparse 两个通道不同的
匹配方式。DESA 使用同一组生成参考段落实现这种通道非对称设计。正交残差扩展
为 Dense 查询补充新的语义方向，分数乘积锚定则利用相同证据，在原始 Sparse
支持集合内部重新排列文档。为避免将方法效果绑定在固定的 top-$L$ 截断上，本文
根据完整的通道排序确定融合结果，并记录认证其有序 top-$K$ 所需的各通道回放
深度。

在七个 BEIR 数据集上，DESA 相对于 Original，将等数据集权重宏平均 nDCG@10
和 Recall@20 分别提高了 3.82\% 和 2.38\%，同时将 Dense 与 Sparse 的回放深度
分别降低了 36.90\% 和 36.56\%。算子分析进一步说明了这些增益的来源：Sparse
anchoring 带来了更稳定的效果提升，Dense residual expansion 则提供了额外增益，
并减少了融合所需的排序证据。在使用相同生成证据的对比中，DESA 以少 64.95\%
的融合侧排名条目，取得了与 QuDAR-simple RRF 相近的检索质量。

这些结果表明，混合检索中的查询扩展需要在两个通道之间形成明确分工。生成证据
在 Dense 检索中用于扩大语义覆盖；在 Sparse 检索中，它与原始查询保持锚定，
从而在不扩大词法支持范围的情况下改善文档排序。这种分工概括了 DESA 的核心
设计原则：Dense 负责扩展，Sparse 负责锚定。
