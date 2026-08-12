from __future__ import annotations

import json
import re
import subprocess
from pathlib import Path

import yaml

from .generation import parse_references
from .io import read_jsonl, sha256_file
from .models import GenerationRecord, QueryResult
from .tiny import run_tiny

SECRET_PATTERNS = (
    re.compile(r"gh[opurs]_[A-Za-z0-9_]{20,}"),
    re.compile(r"sk-[A-Za-z0-9_-]{20,}"),
    re.compile(re.escape("/") + r"Users/[^/\s]+/"),
    re.compile(r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b"),
)


def verify_repository(root: Path) -> dict[str, object]:
    errors: list[str] = []
    artifact_counts = {"generation_records": 0, "query_results": 0, "ranking_stores": 0}
    configs = sorted((root / "configs").rglob("*.yaml"))
    for path in configs:
        value = yaml.safe_load(path.read_text(encoding="utf-8"))
        if not isinstance(value, dict) or value.get("schema_version") != 1:
            errors.append(f"invalid schema_version: {path.relative_to(root)}")
    prompt = root / "prompts" / "primary-reference-v1.txt"
    try:
        parse_references('{"references":["a","b","c","d","e"]}', 5)
    except ValueError as error:
        errors.append(f"generation parser smoke failed: {error}")
    candidates = subprocess.check_output(
        ["git", "ls-files", "--cached", "--others", "--exclude-standard"],
        cwd=root,
        text=True,
    ).splitlines()
    for relative in candidates:
        path = root / relative
        if not path.is_file() or path.suffix in {".lock", ".png", ".npy", ".db"}:
            continue
        try:
            text = path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            continue
        for pattern in SECRET_PATTERNS:
            if pattern.search(text):
                errors.append(f"possible private value in {path.relative_to(root)}")
                break

    generation_root = root / "artifacts" / "generations"
    for path in sorted(generation_root.rglob("*.jsonl")):
        if "compat" in path.parts:
            continue
        try:
            for row in read_jsonl(path):
                GenerationRecord.model_validate(row)
                artifact_counts["generation_records"] += 1
        except Exception as error:
            errors.append(f"invalid generation artifact {path.relative_to(root)}: {error}")

    ranking_root = root / "artifacts" / "rankings"
    for manifest_path in sorted(ranking_root.rglob("rankings*-manifest.json")):
        try:
            manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
            run_id = str(manifest["run_id"])
            store_name = (
                "rankings.sqlite3" if run_id == "primary" else f"rankings-{run_id}.sqlite3"
            )
            store_path = manifest_path.parent / store_name
            if sha256_file(store_path) != manifest["ranking_store_sha256"]:
                raise ValueError("ranking store hash mismatch")
            artifact_counts["ranking_stores"] += 1
        except Exception as error:
            errors.append(
                f"invalid ranking manifest {manifest_path.relative_to(root)}: {error}"
            )

    result_root = root / "artifacts" / "results" / "raw"
    for path in sorted(result_root.rglob("*.jsonl")):
        if "fixed-top-l" in path.name:
            continue
        try:
            for row in read_jsonl(path):
                QueryResult.model_validate(row)
                artifact_counts["query_results"] += 1
        except Exception as error:
            errors.append(f"invalid result artifact {path.relative_to(root)}: {error}")
    for manifest_path in sorted(result_root.rglob("*-manifest.json")):
        try:
            manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
            output_id = str(manifest["output_id"])
            results_path = manifest_path.parent / f"{output_id}.jsonl"
            fixed_path = manifest_path.parent / f"{output_id}-fixed-top-l.jsonl"
            if sha256_file(results_path) != manifest["results_sha256"]:
                raise ValueError("result file hash mismatch")
            if sha256_file(fixed_path) != manifest["fixed_top_l_sha256"]:
                raise ValueError("fixed Top-L file hash mismatch")
        except Exception as error:
            errors.append(f"invalid result manifest {manifest_path.relative_to(root)}: {error}")
    tiny_path = root / "artifacts" / "results" / "aggregated" / "verify-tiny.json"
    tiny = run_tiny(tiny_path)
    if tiny["ordered_top20"] != tiny["replay"]["ordered_top_k"]:
        errors.append("tiny replay parity failed")
    result = {
        "ok": not errors,
        "errors": errors,
        "config_count": len(configs),
        "primary_prompt_sha256": sha256_file(prompt),
        "tiny_record_sha256": tiny["record_sha256"],
        "artifact_counts": artifact_counts,
    }
    if errors:
        raise RuntimeError(json.dumps(result, indent=2))
    return result
