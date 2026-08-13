# Query2doc reproduction card

- Primary source: <https://aclanthology.org/2023.emnlp-main.585/>
- Public reference implementation: no official executable repository identified.

## Formal-v1 interpretation

The paper generates one pseudo-document with a few-shot prompt, concatenates it with
the original query for Dense retrieval, and repeats the original query five times
before the pseudo-document for BM25. Formal-v1 reproduces those two integration rules.

The original demonstrations are MS MARCO examples and the reported generator is a
retired proprietary model. To avoid silently changing demonstrations across models
or introducing an in-domain example advantage, formal-v1 uses a frozen instruction-only
prompt with the common open generator. This is reported as a normalized reproduction;
the deviation is never described as an exact paper reproduction.

The single pseudo-document is emitted as a grammar-constrained one-string JSON array;
the grammar changes only the response container.
