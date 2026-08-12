import json
import zipfile
from pathlib import Path

import pytest

from hybrid_query_construction.datasets import prepare_beir_dataset, unseal_qrels


def _fixture_archive(path: Path) -> None:
    with zipfile.ZipFile(path, "w") as archive:
        archive.writestr(
            "fixture/corpus.jsonl", json.dumps({"_id": "d1", "text": "text"}) + "\n"
        )
        archive.writestr(
            "fixture/queries.jsonl",
            json.dumps({"_id": "q1", "text": "query"})
            + "\n"
            + json.dumps({"_id": "train-only", "text": "excluded"})
            + "\n",
        )
        archive.writestr("fixture/qrels/test.tsv", "query-id\tcorpus-id\tscore\nq1\td1\t1\n")


def test_heldout_qrels_remain_sealed_until_lock(tmp_path: Path) -> None:
    archive = tmp_path / "source.zip"
    _fixture_archive(archive)
    manifest = prepare_beir_dataset(
        "fixture", archive.as_uri(), tmp_path, heldout=True, split="test"
    )
    assert manifest["qrels_state"] == "sealed_in_archive"
    assert manifest["evaluation_query_count"] == 1
    queries = (tmp_path / "data/processed/fixture/queries.jsonl").read_text()
    assert '"q1"' in queries
    assert "train-only" not in queries
    assert not (tmp_path / "data/processed/fixture/qrels.tsv").exists()
    with pytest.raises(RuntimeError):
        unseal_qrels("fixture", tmp_path, tmp_path / "missing-lock.json")


def test_unseal_preserves_the_locked_dataset_manifest(tmp_path: Path) -> None:
    archive = tmp_path / "source.zip"
    _fixture_archive(archive)
    prepare_beir_dataset("fixture", archive.as_uri(), tmp_path, heldout=True, split="test")
    manifest_path = tmp_path / "data/processed/fixture/manifest.json"
    before = manifest_path.read_bytes()
    lock = tmp_path / "lock.json"
    lock.write_text(
        json.dumps(
            {
                "tracked_protocol_files": {},
                "pre_evaluation_artifacts": {},
                "heldout_inputs": {},
            }
        )
    )

    destination = unseal_qrels("fixture", tmp_path, lock)
    assert destination.exists()
    assert manifest_path.read_bytes() == before
    receipt = tmp_path / "artifacts/lock/unsealed-fixture.json"
    assert json.loads(receipt.read_text())["dataset"] == "fixture"
