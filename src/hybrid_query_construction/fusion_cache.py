from __future__ import annotations

import json
import sqlite3
from dataclasses import dataclass
from pathlib import Path

from .fusion import complete_wrrf
from .io import canonical_json, sha256_bytes
from .replay import replay_complete_wrrf

ALGORITHM = "complete-wrrf-replay-v1"


@dataclass(frozen=True)
class CachedFusionReplay:
    ordered_top_k: tuple[str, ...]
    dense_depth: int
    sparse_depth: int
    sparse_exhausted: bool
    trace_sha256: str
    cache_hit: bool


class FusionReplayCache:
    def __init__(self, path: Path) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        self.connection = sqlite3.connect(path)
        self.connection.execute(
            """CREATE TABLE IF NOT EXISTS fusion_replay (
            algorithm TEXT NOT NULL,
            dense_sha256 TEXT NOT NULL,
            sparse_sha256 TEXT NOT NULL,
            top_k INTEGER NOT NULL,
            rrf_constant INTEGER NOT NULL,
            payload TEXT NOT NULL,
            payload_sha256 TEXT NOT NULL,
            PRIMARY KEY (algorithm, dense_sha256, sparse_sha256, top_k, rrf_constant)
            )"""
        )
        self.connection.commit()
        self.hits = 0
        self.misses = 0

    def close(self) -> None:
        self.connection.close()

    def __enter__(self) -> FusionReplayCache:
        return self

    def __exit__(self, *_: object) -> None:
        self.close()

    def get_or_compute(
        self,
        dense: tuple[str, ...],
        sparse: tuple[str, ...],
        *,
        dense_sha256: str,
        sparse_sha256: str,
        top_k: int,
        constant: int,
    ) -> CachedFusionReplay:
        key = (ALGORITHM, dense_sha256, sparse_sha256, top_k, constant)
        row = self.connection.execute(
            """SELECT payload, payload_sha256 FROM fusion_replay
            WHERE algorithm=? AND dense_sha256=? AND sparse_sha256=?
            AND top_k=? AND rrf_constant=?""",
            key,
        ).fetchone()
        if row is not None:
            if sha256_bytes(row[0].encode()) != row[1]:
                raise RuntimeError("cached fusion/replay payload hash mismatch")
            value = json.loads(row[0])
            self.hits += 1
            return CachedFusionReplay(
                ordered_top_k=tuple(value["ordered_top_k"]),
                dense_depth=int(value["dense_depth"]),
                sparse_depth=int(value["sparse_depth"]),
                sparse_exhausted=bool(value["sparse_exhausted"]),
                trace_sha256=str(value["trace_sha256"]),
                cache_hit=True,
            )

        fused = complete_wrrf((dense, sparse), top_k=top_k, constant=constant)
        replay = replay_complete_wrrf(
            dense, sparse, top_k=top_k, constant=constant, keep_trace=True
        )
        if tuple(fused) != replay.ordered_top_k:
            raise AssertionError("replay result does not match complete fusion")
        payload = canonical_json(
            {
                "ordered_top_k": fused,
                "dense_depth": replay.dense_depth,
                "sparse_depth": replay.sparse_depth,
                "sparse_exhausted": replay.sparse_exhausted,
                "trace_sha256": sha256_bytes(canonical_json(replay.trace).encode()),
            }
        )
        self.connection.execute(
            "INSERT INTO fusion_replay VALUES (?, ?, ?, ?, ?, ?, ?)",
            (*key, payload, sha256_bytes(payload.encode())),
        )
        self.connection.commit()
        self.misses += 1
        value = json.loads(payload)
        return CachedFusionReplay(
            ordered_top_k=tuple(value["ordered_top_k"]),
            dense_depth=int(value["dense_depth"]),
            sparse_depth=int(value["sparse_depth"]),
            sparse_exhausted=bool(value["sparse_exhausted"]),
            trace_sha256=str(value["trace_sha256"]),
            cache_hit=False,
        )
