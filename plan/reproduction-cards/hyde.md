# HyDE reproduction card

- Primary source: <https://aclanthology.org/2023.acl-long.99/>
- Official implementation: <https://github.com/texttron/hyde>
- Inspected commit: `a2fd8734307612cb0225d71ffbf26e0d225986b8`
- Repository license observed at inspection: none.

## Formal-v1 interpretation

The public task instructions are adapted only to require strict JSON. Eight
hypothetical passages are generated per draw, matching the official generator's
default sample count. Dense retrieval averages the hypothetical-passage embeddings
and normalizes the result. Sparse remains the
original BM25 query because HyDE is a Dense method.

The eight passages are emitted as one strict JSON record with a 512-token completion
ceiling. This preserves the eight-passage integration while making the open-model
generation call auditable; it is a normalized reproduction rather than an API-level
replica of the original eight-completion request.

The original paper used a different generator and Contriever. Formal-v1 holds the
generator and primary Dense encoder fixed across methods; this row is therefore a
normalized method reproduction, not a numerical reproduction of the paper table.

Released task-specific intents are used for FiQA, ArguAna, SciFact, and TREC-COVID.
The remaining datasets use the released generic web-search intent. The exact rendered
prompt and hash are stored with every generation.
