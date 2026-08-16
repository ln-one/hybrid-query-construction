# Related Work blueprint

### Paragraph 1

- Role: establish the generative query-expansion family.
- Main claim: LLM-generated document-side language supplies missing lexical and
  semantic cues, but its value varies by query, collection, and retriever.
- Evidence: HyDE, Query2doc, Jagerman et al., MuGI, and Weller et al.
- Transition: variable effects motivate separating evaluation conditions from
  integration design.
- Forbidden content: chronological paper-by-paper narration.

### Paragraph 2

- Role: position the evaluation problem.
- Main claim: a fixed top-$L$ cutoff conditions the fused result as well as the
  amount of each ranking read.
- Evidence: MuGI, Exp4Fuse, and EAHR.
- Transition: once cutoff and result semantics are separated, the remaining
  question is how generated evidence should enter each channel.
- Forbidden content: detailed replay mechanics or a claim that DESA introduces
  EAHR's complete-list target.

### Paragraph 3

- Role: synthesize integration strategies.
- Main claim: prior work integrates generated evidence through text,
  representations, term weights, rank fusion, or separate lexical/semantic
  views; DESA studies asymmetric constraints on the same evidence.
- Evidence: Query2doc, MuGI, Word2Passage, Exp4Fuse, and DVCQR.
- Transition: identify the closest dual-perspective formulation.
- Forbidden content: equations or a full DESA method summary.

### Paragraph 4

- Role: direct contemporary comparison.
- Main claim: QuDAR adaptively weights four completed rankings, whereas DESA
  changes how the Dense and Sparse rankings are constructed before fusion.
- Evidence ID: E28.
- Forbidden content: unsupported superiority claims or claims about QuDAR
  beyond its ACL paper.
