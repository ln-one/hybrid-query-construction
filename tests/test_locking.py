from __future__ import annotations

import json
import sqlite3
from pathlib import Path

import pytest

from hybrid_query_construction.io import sha256_file, write_json
from hybrid_query_construction.locking import verify_lock
from hybrid_query_construction.storage import RankingStore, ranking_store_digest


def _fixture_lock(root: Path) -> tuple[Path, Path]:
    directory = root / "artifacts/rankings/toy"
    database = directory / "rankings.sqlite3"
    with RankingStore(database, "toy", ("d1", "d2")) as store:
        store.put(
            query_id="q1",
            draw_id=0,
            track="base",
            channel="dense_original",
            reference_count=0,
            ranking=("d1", "d2"),
            support=2,
            fallback=False,
            generation_sha256="generation",
        )
    manifest_path = directory / "rankings-manifest.json"
    write_json(manifest_path, {"ranking_store_sha256": ranking_store_digest(database)})
    artifacts = {
        str(database.relative_to(root)): sha256_file(database),
        str(manifest_path.relative_to(root)): sha256_file(manifest_path),
    }
    lock_path = root / "artifacts/lock/pre-heldout-v1.json"
    write_json(
        lock_path,
        {
            "tracked_protocol_files": {},
            "pre_evaluation_artifacts": artifacts,
            "model_artifacts": {},
            "heldout_inputs": {},
        },
    )
    return lock_path, database


def test_lock_accepts_sqlite_layout_change_when_logical_digest_matches(
    tmp_path: Path,
) -> None:
    lock_path, database = _fixture_lock(tmp_path)
    locked_file_sha = json.loads(lock_path.read_text())["pre_evaluation_artifacts"][
        str(database.relative_to(tmp_path))
    ]
    connection = sqlite3.connect(database)
    connection.execute(
        "INSERT OR REPLACE INTO metadata(key, value) VALUES('dataset', 'toy')"
    )
    connection.commit()
    connection.close()
    assert sha256_file(database) != locked_file_sha
    verify_lock(tmp_path, lock_path)


def test_lock_rejects_logical_ranking_change(tmp_path: Path) -> None:
    lock_path, database = _fixture_lock(tmp_path)
    with RankingStore(database, "toy", ("d1", "d2")) as store:
        store.put(
            query_id="q2",
            draw_id=0,
            track="base",
            channel="dense_original",
            reference_count=0,
            ranking=("d2", "d1"),
            support=2,
            fallback=False,
            generation_sha256="changed",
        )
    with pytest.raises(RuntimeError, match="artifact changed after lock"):
        verify_lock(tmp_path, lock_path)
