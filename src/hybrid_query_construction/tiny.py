from __future__ import annotations

import tempfile
from pathlib import Path

import numpy as np

from .fusion import complete_wrrf, fixed_top_l_wrrf, rank_scores
from .fusion_cache import FusionReplayCache
from .io import canonical_json, sha256_bytes, write_json
from .methods import orthogonal_residual, sparse_score_product
from .metrics import ndcg_at_k, recall_at_k
from .replay import replay_complete_wrrf
from .storage import RankingStore


def run_tiny(output: Path) -> dict[str, object]:
    document_ids = [f"d{index:02d}" for index in range(30)]
    original = np.asarray([1.0, 0.0, 0.0], dtype=np.float32)
    references = [
        np.asarray([1.0, 1.0, 0.0], dtype=np.float32),
        np.asarray([1.0, 0.0, 1.0], dtype=np.float32),
    ]
    proposed = orthogonal_residual(original, references)
    documents = np.asarray(
        [[1.0, (index % 5) / 5.0, (index % 3) / 3.0] for index in range(30)],
        dtype=np.float32,
    )
    documents /= np.linalg.norm(documents, axis=1, keepdims=True)
    dense_scores = {
        document_id: float(score)
        for document_id, score in zip(document_ids, documents @ proposed, strict=True)
    }
    dense = rank_scores(dense_scores)
    original_sparse = {
        document_id: float(31 - index)
        for index, document_id in enumerate(document_ids)
        if index % 2 == 0
    }
    rewrite_sparse = {
        document_id: float(index + 1)
        for index, document_id in enumerate(document_ids)
        if index % 3 != 0
    }
    anchored = sparse_score_product(original_sparse, rewrite_sparse)
    sparse = rank_scores(anchored)
    top = complete_wrrf((dense, sparse), top_k=20, constant=60)
    replay = replay_complete_wrrf(dense, sparse, top_k=20, constant=60)
    with tempfile.TemporaryDirectory() as temporary:
        temporary_root = Path(temporary)
        source_path = temporary_root / "source.sqlite3"
        reused_path = temporary_root / "reused.sqlite3"
        with RankingStore(source_path, "tiny", document_ids) as source:
            dense_sha = source.put(
                query_id="q0",
                draw_id=0,
                track="base",
                channel="dense_original",
                reference_count=0,
                ranking=dense,
                support=len(dense),
                fallback=False,
                generation_sha256="0" * 64,
            )
            sparse_sha = source.put(
                query_id="q0",
                draw_id=0,
                track="base",
                channel="sparse_original",
                reference_count=0,
                ranking=sparse,
                support=len(sparse),
                fallback=False,
                generation_sha256="0" * 64,
            )
        with RankingStore(reused_path, "tiny", document_ids) as reused:
            reuse_evidence = reused.copy_verified_from(source_path, select=lambda _key: True)
            reused_dense = reused.get(
                query_id="q0",
                draw_id=0,
                track="base",
                channel="dense_original",
                reference_count=0,
            )
        with FusionReplayCache(temporary_root / "fusion.sqlite3") as cache:
            cache.get_or_compute(
                tuple(dense),
                tuple(sparse),
                dense_sha256=dense_sha,
                sparse_sha256=sparse_sha,
                top_k=20,
                constant=60,
            )
            cached = cache.get_or_compute(
                tuple(dense),
                tuple(sparse),
                dense_sha256=dense_sha,
                sparse_sha256=sparse_sha,
                top_k=20,
                constant=60,
            )
    qrels = {"d02": 2, "d04": 1, "d08": 1}
    result: dict[str, object] = {
        "schema_version": 1,
        "fixture": "tiny-v1",
        "ordered_top20": top,
        "replay": replay.model_dump(mode="json"),
        "ndcg_at_10": ndcg_at_k(top, qrels, 10),
        "recall_at_20": recall_at_k(top, qrels, 20),
        "fixed_top20": fixed_top_l_wrrf((dense, sparse), 20, top_k=20, constant=60),
        "reuse": {
            "rankings_verified": reuse_evidence.ordinal_rows_verified,
            "itemwise_equal": reused_dense.ranking == tuple(dense),
            "ranking_sha256_equal": reused_dense.ranking_sha256 == dense_sha,
            "fusion_cache_hit": cached.cache_hit,
            "fusion_cache_top20_equal": list(cached.ordered_top_k) == top,
        },
    }
    result["record_sha256"] = sha256_bytes(canonical_json(result).encode("utf-8"))
    write_json(output, result)
    return result
