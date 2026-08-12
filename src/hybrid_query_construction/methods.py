from __future__ import annotations

from collections.abc import Mapping, Sequence

import numpy as np
from numpy.typing import NDArray

FloatArray = NDArray[np.float32]


def l2_normalize(vector: FloatArray) -> FloatArray:
    norm = float(np.linalg.norm(vector))
    if norm == 0.0:
        raise ValueError("cannot normalize a zero vector")
    return np.asarray(vector / norm, dtype=np.float32)


def contextual_mean(reference_vectors: Sequence[FloatArray]) -> FloatArray:
    if not reference_vectors:
        raise ValueError("at least one reference vector is required")
    return l2_normalize(np.mean(np.stack(reference_vectors), axis=0, dtype=np.float32))


def orthogonal_residual(
    original_vector: FloatArray,
    contextual_reference_vectors: Sequence[FloatArray],
) -> FloatArray:
    """Keep the original unit direction and add only orthogonal reference content."""
    original = l2_normalize(original_vector)
    reference_mean = np.mean(np.stack(contextual_reference_vectors), axis=0, dtype=np.float32)
    residual = reference_mean - np.dot(original, reference_mean) * original
    return l2_normalize(np.asarray(original + residual, dtype=np.float32))


def reference_mean(reference_vectors: Sequence[FloatArray]) -> FloatArray:
    return contextual_mean(reference_vectors)


def sparse_score_product(
    original_scores: Mapping[str, float], rewrite_scores: Mapping[str, float]
) -> dict[str, float]:
    """Multiply scores for documents supported by both Sparse queries."""
    shared = original_scores.keys() & rewrite_scores.keys()
    return {
        document_id: float(original_scores[document_id] * rewrite_scores[document_id])
        for document_id in shared
        if original_scores[document_id] > 0.0 and rewrite_scores[document_id] > 0.0
    }


def sparse_boolean_mask(
    original_scores: Mapping[str, float], rewrite_scores: Mapping[str, float]
) -> dict[str, float]:
    return {
        document_id: float(rewrite_scores[document_id])
        for document_id in original_scores.keys() & rewrite_scores.keys()
        if rewrite_scores[document_id] > 0.0
    }


def primary_sparse_rewrite(query: str, references: Sequence[str]) -> str:
    return " ".join([query.strip(), *(reference.strip() for reference in references)]).strip()


def mugi_sparse_rewrite(query: str, references: Sequence[str], beta: int = 4) -> str:
    if beta <= 0:
        raise ValueError("beta must be positive")
    reference_length = sum(len(reference) for reference in references)
    repetitions = max(1, reference_length // max(1, len(query) * beta))
    return " ".join([*([query.strip()] * repetitions), *references]).strip()


def query2doc_sparse_rewrite(query: str, reference: str) -> str:
    return " ".join([*([query.strip()] * 5), reference.strip()]).strip()
