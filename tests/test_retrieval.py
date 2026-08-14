import json
from pathlib import Path

import numpy as np
import pytest

from hybrid_query_construction.retrieval import dense_ranking, reuse_embedding_matrix


def test_dense_ranking_uses_score_then_document_id_tie_rule() -> None:
    identifiers = ["z", "a", "m"]
    documents = np.asarray([[1.0, 0.0], [1.0, 0.0], [0.0, 1.0]], dtype=np.float32)
    query = np.asarray([1.0, 0.0], dtype=np.float32)
    assert dense_ranking(identifiers, documents, query) == ["a", "z", "m"]


def _write_corpus(path: Path, rows: list[tuple[str, str]]) -> None:
    path.write_text(
        "".join(json.dumps({"_id": key, "text": text}) + "\n" for key, text in rows),
        encoding="utf-8",
    )


def test_reuse_embedding_matrix_supports_verified_subset_and_reordering(
    tmp_path: Path,
) -> None:
    source_corpus = tmp_path / "source.jsonl"
    target_corpus = tmp_path / "target.jsonl"
    source_ids = tmp_path / "source-ids.json"
    source_embeddings = tmp_path / "source.npy"
    _write_corpus(source_corpus, [("d0", "zero"), ("d1", "one"), ("d2", "two")])
    _write_corpus(target_corpus, [("d2", "two"), ("d0", "zero")])
    source_ids.write_text('["d0", "d1", "d2"]\n', encoding="utf-8")
    matrix = np.asarray([[0, 1], [2, 3], [4, 5]], dtype=np.float32)
    np.save(source_embeddings, matrix)

    ids_path, embeddings_path, evidence_path = reuse_embedding_matrix(
        target_corpus,
        source_corpus,
        source_ids,
        source_embeddings,
        tmp_path / "reused",
    )

    assert json.loads(ids_path.read_text()) == ["d2", "d0"]
    np.testing.assert_array_equal(np.load(embeddings_path), matrix[[2, 0]])
    assert json.loads(evidence_path.read_text())["item_text_hashes_verified"] == 2


def test_reuse_embedding_matrix_rejects_changed_text(tmp_path: Path) -> None:
    source_corpus = tmp_path / "source.jsonl"
    target_corpus = tmp_path / "target.jsonl"
    source_ids = tmp_path / "source-ids.json"
    source_embeddings = tmp_path / "source.npy"
    _write_corpus(source_corpus, [("d0", "zero")])
    _write_corpus(target_corpus, [("d0", "changed")])
    source_ids.write_text('["d0"]\n', encoding="utf-8")
    np.save(source_embeddings, np.asarray([[0, 1]], dtype=np.float32))

    with pytest.raises(RuntimeError, match="text differs"):
        reuse_embedding_matrix(
            target_corpus,
            source_corpus,
            source_ids,
            source_embeddings,
            tmp_path / "reused",
        )
