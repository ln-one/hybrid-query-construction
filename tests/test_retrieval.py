import numpy as np

from hybrid_query_construction.retrieval import dense_ranking


def test_dense_ranking_uses_score_then_document_id_tie_rule() -> None:
    identifiers = ["z", "a", "m"]
    documents = np.asarray([[1.0, 0.0], [1.0, 0.0], [0.0, 1.0]], dtype=np.float32)
    query = np.asarray([1.0, 0.0], dtype=np.float32)
    assert dense_ranking(identifiers, documents, query) == ["a", "z", "m"]
