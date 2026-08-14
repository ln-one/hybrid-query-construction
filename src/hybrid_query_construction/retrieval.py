from __future__ import annotations

import json
import subprocess
import sys
from collections.abc import Sequence
from pathlib import Path

import numpy as np
from numpy.typing import NDArray
from sentence_transformers import SentenceTransformer

from .datasets import iter_corpus
from .fusion import rank_scores
from .io import atomic_write_text, canonical_json, sha256_bytes, sha256_file, write_json


class DenseEncoder:
    def __init__(self, model_id: str, revision: str, device: str = "mps") -> None:
        self.model = SentenceTransformer(model_id, revision=revision, device=device)
        self.model.max_seq_length = 512

    def encode_documents(
        self, texts: Sequence[str], batch_size: int = 128
    ) -> NDArray[np.float32]:
        return np.asarray(
            self.model.encode(
                list(texts),
                batch_size=batch_size,
                normalize_embeddings=True,
                show_progress_bar=True,
            ),
            dtype=np.float32,
        )

    def encode_queries(
        self, texts: Sequence[str], instruction: str, batch_size: int = 128
    ) -> NDArray[np.float32]:
        instructed = [instruction + text for text in texts]
        return np.asarray(
            self.model.encode(
                instructed,
                batch_size=batch_size,
                normalize_embeddings=True,
                show_progress_bar=False,
            ),
            dtype=np.float32,
        )


def dense_ranking(
    document_ids: Sequence[str],
    document_embeddings: NDArray[np.float32],
    query_embedding: NDArray[np.float32],
) -> list[str]:
    scores = document_embeddings @ query_embedding
    identifiers = np.asarray(document_ids, dtype=str)
    order = np.lexsort((identifiers, -scores))
    return [document_ids[int(index)] for index in order]


def prepare_lucene_collection(corpus_path: Path, output_directory: Path) -> tuple[Path, int]:
    output_directory.mkdir(parents=True, exist_ok=True)
    destination = output_directory / "docs.jsonl"
    rows = []
    count = 0
    for document_id, contents in iter_corpus(corpus_path):
        rows.append(json.dumps({"id": document_id, "contents": contents}, ensure_ascii=False))
        count += 1
    atomic_write_text(destination, "\n".join(rows) + "\n")
    return destination, count


def build_lucene_index(
    collection_directory: Path, index_directory: Path, threads: int = 8
) -> None:
    if index_directory.exists() and any(index_directory.iterdir()):
        return
    index_directory.parent.mkdir(parents=True, exist_ok=True)
    subprocess.run(
        [
            sys.executable,
            "-m",
            "pyserini.index.lucene",
            "--collection",
            "JsonCollection",
            "--input",
            str(collection_directory),
            "--index",
            str(index_directory),
            "--generator",
            "DefaultLuceneDocumentGenerator",
            "--threads",
            str(threads),
            "--storeRaw",
        ],
        check=True,
    )


class SparseSearcher:
    def __init__(self, index_directory: Path, k1: float, b: float, corpus_size: int) -> None:
        from pyserini.search.lucene import LuceneSearcher

        self.searcher = LuceneSearcher(str(index_directory))
        self.searcher.set_bm25(k1, b)
        self.corpus_size = corpus_size

    def scores(self, query: str) -> dict[str, float]:
        hits = self.searcher.search(query, k=self.corpus_size)
        return {str(hit.docid): float(hit.score) for hit in hits if hit.score > 0.0}

    def ranking(self, query: str) -> list[str]:
        return rank_scores(self.scores(query))


def save_embedding_matrix(
    corpus_path: Path,
    encoder: DenseEncoder,
    output_directory: Path,
    batch_size: int = 128,
) -> tuple[Path, Path]:
    output_directory.mkdir(parents=True, exist_ok=True)
    ids_path = output_directory / "document_ids.json"
    embeddings_path = output_directory / "document_embeddings.npy"
    if ids_path.exists() and embeddings_path.exists():
        return ids_path, embeddings_path
    documents = list(iter_corpus(corpus_path))
    identifiers = [document_id for document_id, _ in documents]
    embeddings = encoder.encode_documents(
        [text for _, text in documents], batch_size=batch_size
    )
    atomic_write_text(ids_path, json.dumps(identifiers, ensure_ascii=False) + "\n")
    np.save(embeddings_path, embeddings)
    return ids_path, embeddings_path


def reuse_embedding_matrix(
    corpus_path: Path,
    source_corpus_path: Path,
    source_ids_path: Path,
    source_embeddings_path: Path,
    output_directory: Path,
) -> tuple[Path, Path, Path]:
    """Materialize an exact subset/reordering of an existing embedding matrix."""
    output_directory.mkdir(parents=True, exist_ok=True)
    ids_path = output_directory / "document_ids.json"
    embeddings_path = output_directory / "document_embeddings.npy"
    evidence_path = output_directory / "reuse-evidence.json"
    if ids_path.exists() and embeddings_path.exists() and evidence_path.exists():
        evidence = json.loads(evidence_path.read_text(encoding="utf-8"))
        if evidence["target_ids_sha256"] != sha256_file(ids_path):
            raise RuntimeError("reused embedding identifier hash mismatch")
        if evidence["target_embeddings_sha256"] != sha256_file(embeddings_path):
            raise RuntimeError("reused embedding matrix hash mismatch")
        return ids_path, embeddings_path, evidence_path

    source_ids = json.loads(source_ids_path.read_text(encoding="utf-8"))
    if len(source_ids) != len(set(source_ids)):
        raise RuntimeError("source embedding identifiers are not unique")
    source_ordinals = {document_id: index for index, document_id in enumerate(source_ids)}
    source_text_hashes = {
        document_id: sha256_bytes(text.encode())
        for document_id, text in iter_corpus(source_corpus_path)
    }
    if set(source_ordinals) != set(source_text_hashes):
        raise RuntimeError("source corpus and embedding identifiers differ")

    target_ids: list[str] = []
    target_ordinals: list[int] = []
    for document_id, text in iter_corpus(corpus_path):
        if document_id not in source_ordinals:
            raise RuntimeError(f"target document missing from embedding source: {document_id}")
        if source_text_hashes[document_id] != sha256_bytes(text.encode()):
            raise RuntimeError(f"target document text differs from source: {document_id}")
        target_ids.append(document_id)
        target_ordinals.append(source_ordinals[document_id])

    source_embeddings = np.load(source_embeddings_path, mmap_mode="r")
    if source_embeddings.shape[0] != len(source_ids):
        raise RuntimeError("source embedding row count does not match identifiers")
    target_embeddings = np.asarray(
        source_embeddings[np.asarray(target_ordinals, dtype=np.int64)], dtype=np.float32
    )
    atomic_write_text(ids_path, json.dumps(target_ids, ensure_ascii=False) + "\n")
    np.save(embeddings_path, target_embeddings)
    write_json(
        evidence_path,
        {
            "schema_version": 1,
            "source_corpus_sha256": sha256_file(source_corpus_path),
            "source_ids_sha256": sha256_file(source_ids_path),
            "source_embeddings_sha256": sha256_file(source_embeddings_path),
            "target_corpus_sha256": sha256_file(corpus_path),
            "target_ids_sha256": sha256_file(ids_path),
            "target_embeddings_sha256": sha256_file(embeddings_path),
            "target_rows": len(target_ids),
            "source_ordinals_sha256": sha256_bytes(canonical_json(target_ordinals).encode()),
            "item_text_hashes_verified": len(target_ids),
        },
    )
    return ids_path, embeddings_path, evidence_path
