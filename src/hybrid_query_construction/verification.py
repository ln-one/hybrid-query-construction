from __future__ import annotations

import json
import re
import subprocess
from pathlib import Path

import yaml

from .generation import parse_references
from .io import sha256_file
from .tiny import run_tiny

SECRET_PATTERNS = (
    re.compile(r"gh[opurs]_[A-Za-z0-9_]{20,}"),
    re.compile(r"sk-[A-Za-z0-9_-]{20,}"),
    re.compile(re.escape("/") + r"Users/[^/\s]+/"),
    re.compile(r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b"),
)


def verify_repository(root: Path) -> dict[str, object]:
    errors: list[str] = []
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
    }
    if errors:
        raise RuntimeError(json.dumps(result, indent=2))
    return result
