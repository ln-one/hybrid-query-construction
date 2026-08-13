# MuGI reproduction card

- Primary source: <https://aclanthology.org/2024.findings-emnlp.103/>
- Official implementation: <https://github.com/lezhang7/Retrieval_MuGI>
- Inspected commit: `51985aa09a05cfefb3f2098b3eedd8b08283307f`
- Repository license observed at inspection: none.

## Formal-v1 interpretation

MuGI generates several pseudo-references. For Sparse retrieval, its public code repeats
the original query `floor(total_reference_characters / query_characters / beta)` times
and appends the references; formal-v1 fixes `beta=4`. For Dense retrieval, formal-v1
uses contextual feature pooling: each query-reference pair is encoded and the vectors
are averaged and normalized.

The feedback-calibration stage is excluded because the planned comparison concerns
query construction before retrieval. The row is named `mugi`, but the report explicitly
qualifies it as MuGI integration without pseudo-relevance-feedback calibration.

The zero-shot passage intent from the public code is adapted to an exact-length JSON
array. All five passages are generated in one response under the same frozen generator
used by the proposed method. The grammar constrains serialization only.
