from __future__ import annotations

import json
import subprocess
from datetime import UTC, datetime
from pathlib import Path

from .io import sha256_file, write_json

TRACKED_LOCK_PREFIXES = ("configs/", "prompts/", "src/", "scripts/", "plan/")
HELDOUT_DATASETS = ("fiqa", "arguana", "webis-touche2020", "scidocs")
POSTHELDOUT_MAINTENANCE = "plan/postheldout-maintenance-v1.json"


def _git(root: Path, *arguments: str) -> str:
    return subprocess.check_output(["git", *arguments], cwd=root, text=True).strip()


def create_preheldout_lock(root: Path, output: Path) -> dict[str, object]:
    from .audit import formal_progress

    status = _git(root, "status", "--porcelain", "--untracked-files=all")
    if status:
        raise RuntimeError("tracked protocol must be committed before pre-held-out lock")
    heldout_qrels = [
        root / "data" / "processed" / dataset / "qrels.tsv" for dataset in HELDOUT_DATASETS
    ]
    if any(path.exists() for path in heldout_qrels):
        raise RuntimeError("held-out qrels already extracted; lock cannot be created")
    formal_progress(root, require_complete=True)
    tracked = _git(root, "ls-files").splitlines()
    files = {
        relative: sha256_file(root / relative)
        for relative in tracked
        if relative.startswith(TRACKED_LOCK_PREFIXES) or relative == "uv.lock"
    }
    generated = {}
    for directory in (root / "artifacts" / "generations", root / "artifacts" / "rankings"):
        for path in sorted(directory.rglob("*")):
            if path.is_file() and path.name != ".gitkeep":
                generated[str(path.relative_to(root))] = sha256_file(path)
    model_artifacts = {}
    for directory in sorted((root / "data" / "cache" / "models").glob("*-mlx-bf16")):
        for path in sorted(directory.rglob("*")):
            if path.is_file():
                model_artifacts[str(path.relative_to(root))] = sha256_file(path)
    heldout_inputs = {}
    for dataset in HELDOUT_DATASETS:
        for name in ("corpus.jsonl", "queries.jsonl", "manifest.json"):
            path = root / "data" / "processed" / dataset / name
            if not path.exists():
                raise RuntimeError(f"held-out input is missing: {path}")
            heldout_inputs[str(path.relative_to(root))] = sha256_file(path)
        archive = root / "data" / "cache" / f"{dataset}.zip"
        if not archive.exists():
            raise RuntimeError(f"held-out source archive is missing: {archive}")
        heldout_inputs[str(archive.relative_to(root))] = sha256_file(archive)
    manifest: dict[str, object] = {
        "schema_version": 1,
        "protocol_version": "hqc-formal-v1",
        "created_at_utc": datetime.now(UTC).isoformat(),
        "code_commit": _git(root, "rev-parse", "HEAD"),
        "tracked_protocol_files": files,
        "heldout_inputs": heldout_inputs,
        "pre_evaluation_artifacts": generated,
        "model_artifacts": model_artifacts,
        "heldout_qrels_absent": True,
    }
    write_json(output, manifest)
    manifest["manifest_sha256"] = sha256_file(output)
    return manifest


def _approved_protocol_hashes(root: Path, lock_path: Path) -> dict[str, str]:
    maintenance_path = root / POSTHELDOUT_MAINTENANCE
    if not maintenance_path.exists():
        return {}
    maintenance = json.loads(maintenance_path.read_text(encoding="utf-8"))
    if maintenance.get("schema_version") != 1:
        raise RuntimeError("unsupported post-held-out maintenance schema")
    if maintenance.get("preheldout_lock_sha256") != sha256_file(lock_path):
        raise RuntimeError("post-held-out maintenance references a different lock")
    approved = maintenance.get("approved_protocol_file_sha256", {})
    if not isinstance(approved, dict) or not all(
        isinstance(key, str) and isinstance(value, str)
        for key, value in approved.items()
    ):
        raise RuntimeError("invalid approved protocol hashes in maintenance record")
    return approved


def _ranking_database_relative(relative: str) -> str | None:
    if not relative.startswith("artifacts/rankings/"):
        return None
    if relative.endswith(".sqlite3"):
        return relative
    for suffix in (".sqlite3-wal", ".sqlite3-shm"):
        if relative.endswith(suffix):
            return relative[: -len(suffix)] + ".sqlite3"
    return None


def _ranking_manifest_relative(database_relative: str) -> str:
    return database_relative.removesuffix(".sqlite3") + "-manifest.json"


def _logical_ranking_store_matches(
    root: Path,
    relative: str,
    locked_artifacts: dict[str, str],
    verified_databases: dict[str, bool],
) -> bool:
    database_relative = _ranking_database_relative(relative)
    if database_relative is None:
        return False
    if database_relative in verified_databases:
        return verified_databases[database_relative]
    manifest_relative = _ranking_manifest_relative(database_relative)
    locked_manifest_sha = locked_artifacts.get(manifest_relative)
    manifest_path = root / manifest_relative
    database_path = root / database_relative
    if (
        locked_manifest_sha is None
        or not manifest_path.exists()
        or not database_path.exists()
        or sha256_file(manifest_path) != locked_manifest_sha
    ):
        verified_databases[database_relative] = False
        return False
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    expected = manifest.get("ranking_store_sha256")
    if not isinstance(expected, str):
        verified_databases[database_relative] = False
        return False
    from .storage import ranking_store_digest

    matches = ranking_store_digest(database_path) == expected
    verified_databases[database_relative] = matches
    return matches


def verify_lock(root: Path, lock_path: Path) -> None:
    manifest = json.loads(lock_path.read_text(encoding="utf-8"))
    approved_protocol = _approved_protocol_hashes(root, lock_path)
    for relative, expected in manifest["tracked_protocol_files"].items():
        actual = sha256_file(root / relative)
        if actual != expected and actual != approved_protocol.get(relative):
            raise RuntimeError(f"protocol file changed after lock: {relative}")
    locked_artifacts = manifest["pre_evaluation_artifacts"]
    verified_databases: dict[str, bool] = {}
    for relative, expected in locked_artifacts.items():
        path = root / relative
        actual = sha256_file(path) if path.exists() else None
        if actual != expected and not _logical_ranking_store_matches(
            root, relative, locked_artifacts, verified_databases
        ):
            raise RuntimeError(f"artifact changed after lock: {relative}")
    for relative, expected in manifest.get("model_artifacts", {}).items():
        actual = sha256_file(root / relative)
        if actual != expected:
            raise RuntimeError(f"model artifact changed after lock: {relative}")
    for relative, expected in manifest["heldout_inputs"].items():
        actual = sha256_file(root / relative)
        if actual != expected:
            raise RuntimeError(f"held-out input changed after lock: {relative}")
