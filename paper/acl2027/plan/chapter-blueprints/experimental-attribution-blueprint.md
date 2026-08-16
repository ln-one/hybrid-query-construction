# Experimental Attribution Blueprint

### Paragraph 1: evaluation protocol
- Role: define the fixed-Top-$L$ and complete-fusion estimands.
- Main claim: the paper uses nDCG/Recall and equally weighted WRRF.
- Evidence IDs: E21, E27.
- Transition: from evaluated result to datasets and retrievers.
- Forbidden content: new claims about method superiority.

### Paragraph 2: datasets
- Role: identify the exact seven-dataset default scope and upstream sources.
- Main claim: all primary controlled and mechanism results use seven BEIR
  collections; four-dataset numbers are explicitly labeled common subsets.
- Evidence IDs: E12--E19.
- Transition: explain task diversity without enumerating dataset statistics.
- Forbidden content: calling all seven qrels-sealed or held out.

### Paragraph 3: models and retrieval
- Role: attribute generator, dense encoders, sparse scorer, and implementation.
- Main claim: the exact experimental components are standard public releases.
- Evidence IDs: E20, E22--E26.
- Transition: comparison methods follow.
- Forbidden content: model-performance claims not needed for reproducibility.

### Limitations paragraph
- Role: bound the empirical and operational claims.
- Main claim: evidence is limited to English BEIR collections, two generators,
  two dense encoders, BM25, WRRF Top-20 certification, and offline logical
  replay; generation and incomplete judgments create additional uncertainty.
- Evidence IDs: E12, E20--E26.
- Forbidden content: defensive language or new experiments.
