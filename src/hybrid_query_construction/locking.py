from __future__ import annotations

import json
import subprocess
from datetime import UTC, datetime
from pathlib import Path

from .io import sha256_file, write_json

TRACKED_LOCK_PREFIXES = ("configs/", "prompts/", "src/", "scripts/", "plan/")
HELDOUT_DATASETS = ("fiqa", "arguana", "webis-touche2020", "scidocs")


def _git(root: Path, *arguments: str) -> str:
    return subprocess.check_output(["git", *arguments], cwd=root, text=True).strip()


def create_preheldout_lock(root: Path, output: Path) -> dict[str, object]:
    status = _git(root, "status", "--porcelain", "--untracked-files=all")
    if status:
        raise RuntimeError("tracked protocol must be committed before pre-held-out lock")
    heldout_qrels = [
        root / "data" / "processed" / dataset / "qrels.tsv" for dataset in HELDOUT_DATASETS
    ]
    if any(path.exists() for path in heldout_qrels):
        raise RuntimeError("held-out qrels already extracted; lock cannot be created")
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
        "heldout_qrels_absent": True,
    }
    write_json(output, manifest)
    manifest["manifest_sha256"] = sha256_file(output)
    return manifest


def verify_lock(root: Path, lock_path: Path) -> None:
    manifest = json.loads(lock_path.read_text(encoding="utf-8"))
    for relative, expected in manifest["tracked_protocol_files"].items():
        actual = sha256_file(root / relative)
        if actual != expected:
            raise RuntimeError(f"protocol file changed after lock: {relative}")
    for relative, expected in manifest["pre_evaluation_artifacts"].items():
        actual = sha256_file(root / relative)
        if actual != expected:
            raise RuntimeError(f"artifact changed after lock: {relative}")
    for relative, expected in manifest["heldout_inputs"].items():
        actual = sha256_file(root / relative)
        if actual != expected:
            raise RuntimeError(f"held-out input changed after lock: {relative}")
