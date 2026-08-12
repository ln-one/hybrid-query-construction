# Data boundary

`scripts/download_data.py` downloads official BEIR archives and initially extracts
only corpus and query files. Held-out qrels remain inside their original archives
until a pre-held-out lock manifest is successfully written.

Corpora, qrels, indices, and model weights are not committed. Their source URLs,
licenses, sizes, and hashes are recorded in `data/manifest.lock.json`.

