# Data boundary

The preparation command downloads official BEIR archives and initially extracts the
corpus plus queries belonging to the configured evaluation split. It reads only qrels
query-ID membership to select that split. Held-out qrel document IDs and grades remain
inside their original archives until a pre-held-out lock manifest is successfully
written.

Corpora, qrels, indices, and model weights are not committed. Their source URLs,
licenses, sizes, and hashes are recorded in each processed dataset manifest.
