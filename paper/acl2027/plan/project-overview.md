# ACL manuscript overview

## Paper objective

Show that fixed Top-$L$ evaluation confounds the measured effect of LLM query
expansion with an arbitrary truncation choice, then introduce and evaluate
DESA (Dense Expansion and Sparse Anchoring), a channel-asymmetric construction
in which Dense expands and Sparse anchors.

## Argument

1. Query expansion is usually evaluated under a preset Top-$L$.
2. Top-$L$ changes both the fused result and the accessed ranking evidence.
3. Complete-list quality and channel-specific stopping depth separate these
   two effects.
4. Generated evidence should enter Dense and Sparse differently.
5. Orthogonal residual expansion and score-product anchoring improve quality
   while reducing both stopping depths relative to the original query.

## Current scope

- Venue format: ACL main-paper format, eight pages excluding references and
  appendices.
- Draft language: English, reviewed paragraph by paragraph from the Chinese
  argument developed with the author.
- Empirical claims: only values traceable to frozen formal-run artifacts.
- Results chapter: report positive, mixed, and negative outcomes without
  filtering.
