# HyDE reproduction card

- Primary source: <https://aclanthology.org/2023.acl-long.99/>
- Official implementation: <https://github.com/texttron/hyde>
- Inspected commit: `a2fd8734307612cb0225d71ffbf26e0d225986b8`
- Repository license observed at inspection: none.

## Formal-v1 interpretation

The public task instruction is adapted only to require strict JSON. One hypothetical
passage is generated per draw. Dense retrieval averages the original query embedding
and hypothetical-passage embedding, then normalizes the result. Sparse remains the
original BM25 query because HyDE is a Dense method.

The original paper used a different generator and Contriever. Formal-v1 holds the
generator and primary Dense encoder fixed across methods; this row is therefore a
normalized method reproduction, not a numerical reproduction of the paper table.

For FiQA and ArguAna, the released task-specific intent is used (financial answer and
counterargument, respectively). The remaining datasets use the released generic web
search intent. The exact rendered prompt and hash are stored with every generation.

