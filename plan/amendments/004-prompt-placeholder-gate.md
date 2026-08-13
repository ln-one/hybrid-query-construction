# Amendment 004 — substantive-output prompt gate

## Decision

Literal JSON placeholders were removed from every formal prompt. Each prompt now
specifies the required array length in prose and requires every item to contain a
substantive passage. The structured-output grammar still constrains only JSON syntax
and array length; the strict parser still enforces non-empty, distinct strings.

The compatibility gate now covers the primary prompt with both Qwen and Mistral and
every MuGI, Query2doc, and dataset-specific HyDE prompt with Qwen. Each prompt must
produce two exactly reproducible 24-record runs with zero final failures. Any
deterministic retries remain part of the record and are reported.

## Reason

The first pre-lock MuGI run copied the literal `"..."` strings shown in its output
template. Among the first 192 SciFact records, 11 required a retry and two still
failed. This behavior measures prompt-template imitation rather than the published
retrieval method and would unfairly weaken the baseline. The same placeholder was
present in Query2doc and HyDE prompts even though they had not yet been run formally.

The interrupted records are retained locally as diagnostic evidence and excluded
from the formal corpus. All affected generation artifacts are regenerated from the
new committed prompt hashes.

This amendment was made before the pre-held-out lock and before any held-out
relevance grade or judged document identifier was exposed.
