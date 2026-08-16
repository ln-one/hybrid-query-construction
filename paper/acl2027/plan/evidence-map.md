# Evidence Map: Experimental Attribution and Limitations

| ID | Source | Usable fact | Supported manuscript claim | Citation slot | Risk |
|---|---|---|---|---|---|
| E12 | Thakur et al. (2021), BEIR | BEIR standardizes heterogeneous retrieval datasets and evaluation | The seven evaluation collections use the public BEIR releases | Experiments: datasets | none |
| E13 | Wadden et al. (2020) | Introduces SciFact | SciFact source attribution | Experiments: datasets | none |
| E14 | Boteva et al. (2016) | Introduces NFCorpus | NFCorpus source attribution | Experiments: datasets | none |
| E15 | Voorhees et al. (2020) | Introduces TREC-COVID | TREC-COVID source attribution | Experiments: datasets | none |
| E16 | Maia et al. (2018) | Introduces FiQA | FiQA source attribution | Experiments: datasets | none |
| E17 | Wachsmuth et al. (2018) | Introduces ArguAna | ArguAna source attribution | Experiments: datasets | none |
| E18 | Bondarenko et al. (2020) | Introduces Touch\'e 2020 | Touch\'e source attribution | Experiments: datasets | none |
| E19 | Cohan et al. (2020) | Introduces SCIDOCS | SCIDOCS source attribution | Experiments: datasets | none |
| E20 | Robertson and Zaragoza (2009) | Defines BM25 | Sparse retriever attribution | Experiments: retrieval setup | none |
| E21 | Cormack et al. (2009) | Introduces RRF | WRRF attribution | Method/evaluation protocol | none |
| E22 | Lin et al. (2021) | Documents Pyserini | Pyserini attribution | Experiments: retrieval setup | none |
| E23 | Xiao et al. (2023) | Releases BGE resources | BGE encoder attribution | Experiments: retrieval setup | none |
| E24 | Izacard et al. (2022) | Introduces Contriever | Robustness encoder attribution | Experiments: retrieval setup | none |
| E25 | Qwen Team (2024) | Documents Qwen2.5 | Primary generator attribution | Experiments: retrieval setup | none |
| E26 | Jiang et al. (2023) | Documents Mistral 7B Instruct | Second generator attribution | Experiments: retrieval setup | none |
| E27 | J\"arvelin and Kek\"al\"ainen (2002) | Defines cumulative-gain evaluation | nDCG attribution | Experiments: evaluation protocol | none |
| E28 | Kim et al. (2026), QuDAR | Treats original/expanded queries and sparse/dense retrievers as four signals and assigns query-specific fusion weights | Position DESA against query-wise dual-perspective adaptive retrieval | Related Work: channel integration | none |
| E29 | `report/fixed-top-l-query-diagnostics.csv`; `report/fixed-top-l-conclusion-changes.csv` | Fixed cutoffs alter ordered Top-20 outputs and the sign of paired query-level effectiveness differences | Quantify the practical fixed-$L$ sensitivity beyond small macro crossings | Results: fixed cutoffs; Appendix diagnostics | Query--draw rates are descriptive, not significance tests |
| E30 | `report/operator-control-results.csv`; `report/operator-control-paired-tests.csv` | Residual projection is quality-neutral relative to contextual Dense expansion; Sparse product shows a nonsignificant positive nDCG trend relative to an unanchored rewrite | Delimit the functional role of each operator without claiming independent dominance | Results: channel operators; Appendix controls | Only the joint DESA-vs-Shared nDCG gain is confirmatory |
| E31 | `report/qudar-baseline-results.csv`; `report/qudar-paired-tests.csv`; official QuDAR code at commit `0702721e82799d0489850d3f94ac787da43436ad` | Matched-evidence QuDAR-simple RRF is statistically comparable in quality; DESA reads 1,402.1 rather than 4,000 fusion rank entries on average | Direct recent-baseline comparison and fusion-access trade-off | Results: recent methods; Appendix QuDAR table | Rank-based QuDAR-simple only; no end-to-end latency claim |

Each source was checked against an official proceedings page, an author-hosted
paper, or its primary arXiv/OpenReview record before insertion.
