# Amendment 005 — grammar-owned termination

## Decision

Formal generation no longer registers the literal closing bracket `]` as a stop
sequence. XGrammar owns the complete JSON-array syntax and, after accepting the
closing bracket, the logits processor permits only the model EOS token. The strict
parser and one deterministic retry remain unchanged.

The retry instruction also describes the required array in prose instead of showing
literal placeholder strings.

No prompt displays or emphasizes a literal closing bracket. The strict parser rejects
whitespace-only, punctuation-only, and placeholder strings, making the substantive
passage requirement executable rather than advisory.

## Reason

The literal stop sequence competed with the JSON grammar. A closing bracket is valid
text inside a JSON string, so MLX-LM could stop when a passage happened to emit that
token before its closing quote. The first Query2doc compatibility run exposed this as
an unterminated string ending in `]]`. Grammar-owned termination removes the competing
condition and preserves the exact-length structural constraint.

The first SciFact-HyDE compatibility run then showed the complementary failure mode:
the model copied the prominently mentioned closing bracket into repeated string
items. Removing model-visible JSON punctuation and validating substantive content
eliminates that template-imitation channel.

Compatibility permits the preregistered deterministic retry but requires zero final
failures and exact agreement between both runs. Retry counts remain explicit and are
reported as generation cost rather than silently discarded.

This amendment was made before the pre-held-out lock and before any held-out
relevance grade or judged document identifier was exposed.
