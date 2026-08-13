# Amendment 003 — grammar-constrained generation records

## Decision

Formal generation uses `xgrammar==0.2.1` with its MLX Metal logits processor and
an exact-length JSON schema. For a requested count `n`, the model must emit one JSON
array containing exactly `n` strings. Each batched query/draw owns an independent
grammar matcher. The raw constrained completion, backend name, backend version,
model revision, seed, and decoding settings are stored in every generation record.

The grammar restricts JSON structure and array length only. It does not prescribe
the strings, select passages, repair completions, or replace stochastic sampling.
The parser remains strict: strings must also be non-empty and distinct after Unicode
normalization. One same-seed retry remains available for semantic validation failure.

## Reason

The original prompt-only compatibility run produced valid content in malformed
containers: too few items, repeated object keys, copied query identifiers, and extra
closing characters. On the first 120 formal SciFact records, 14 records (11.7%) still
failed after the allowed retry. Falling back to Original at that rate would confound
method comparisons with avoidable serialization failures.

Two preregistration-stage prompt alternatives were rejected before held-out qrels
were unsealed. A more explicit object prompt did not reduce failures, and a top-level
array prompt was often interpreted as five separate one-item arrays. These diagnostic
artifacts are excluded from the formal corpus but retained locally under ignored
preformal storage.

## Compatibility evidence

With grammar-constrained decoding, 24/24 records in the small gate and 120/120 records
in the expanded SciFact gate parsed on the first attempt, each with exactly five
distinct strings. The formal run still requires two exact-reconstruction gates for
both Qwen and Mistral after this amendment is committed.

This amendment was made before the pre-held-out lock and before any held-out relevance
grade or judged document identifier was exposed.
