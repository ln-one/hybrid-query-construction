from __future__ import annotations

import importlib.metadata
import json
from pathlib import Path
from typing import Any

from huggingface_hub import snapshot_download

from .io import canonical_json, sha256_bytes, sha256_file, write_json


def model_artifact_manifest_path(model_directory: Path) -> Path:
    return model_directory / "hqc-model-manifest.json"


def _file_hashes(model_directory: Path) -> dict[str, str]:
    return {
        str(path.relative_to(model_directory)): sha256_file(path)
        for path in sorted(model_directory.rglob("*"))
        if path.is_file() and path.name != "hqc-model-manifest.json"
    }


def write_model_artifact_manifest(
    model_directory: Path,
    *,
    model_id: str,
    revision: str,
    dtype: str,
) -> dict[str, Any]:
    config = json.loads((model_directory / "config.json").read_text(encoding="utf-8"))
    if config.get("torch_dtype") != dtype:
        raise RuntimeError(
            f"converted model dtype mismatch: {config.get('torch_dtype')} != {dtype}"
        )
    files = _file_hashes(model_directory)
    manifest: dict[str, Any] = {
        "schema_version": 1,
        "model_id": model_id,
        "source_revision": revision,
        "dtype": dtype,
        "quantized": False,
        "backend": "mlx_lm",
        "backend_version": importlib.metadata.version("mlx-lm"),
        "files": files,
    }
    manifest["artifact_sha256"] = sha256_bytes(canonical_json(manifest).encode())
    write_json(model_artifact_manifest_path(model_directory), manifest)
    return manifest


def verify_model_artifact(model_directory: Path) -> dict[str, Any]:
    path = model_artifact_manifest_path(model_directory)
    manifest = json.loads(path.read_text(encoding="utf-8"))
    artifact_sha256 = manifest.pop("artifact_sha256")
    if sha256_bytes(canonical_json(manifest).encode()) != artifact_sha256:
        raise RuntimeError(f"model artifact manifest digest mismatch: {path}")
    for relative, expected in manifest["files"].items():
        if sha256_file(model_directory / relative) != expected:
            raise RuntimeError(f"converted model file hash mismatch: {relative}")
    manifest["artifact_sha256"] = artifact_sha256
    return manifest


def convert_model(
    model_directory: Path,
    *,
    model_id: str,
    revision: str,
    dtype: str,
    adopt_existing: bool = False,
) -> dict[str, Any]:
    if model_artifact_manifest_path(model_directory).exists():
        manifest = verify_model_artifact(model_directory)
        expected = (model_id, revision, dtype, "mlx_lm")
        actual = (
            manifest["model_id"],
            manifest["source_revision"],
            manifest["dtype"],
            manifest["backend"],
        )
        if actual != expected:
            raise RuntimeError(f"existing model artifact does not match request: {actual}")
        return manifest
    if model_directory.exists() and any(model_directory.iterdir()):
        if not adopt_existing:
            raise RuntimeError(
                f"unregistered converted model directory exists: {model_directory}"
            )
        return write_model_artifact_manifest(
            model_directory, model_id=model_id, revision=revision, dtype=dtype
        )

    from mlx_lm import convert

    source = Path(snapshot_download(model_id, revision=revision))
    convert(str(source), mlx_path=str(model_directory), dtype=dtype)
    return write_model_artifact_manifest(
        model_directory, model_id=model_id, revision=revision, dtype=dtype
    )
