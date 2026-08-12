from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

FIELDS = (
    "query_id",
    "draw_id",
    "prompt_sha256",
    "model_id",
    "model_revision",
    "backend",
    "backend_version",
    "model_artifact_sha256",
    "seed",
    "decoding",
    "raw_text",
    "parsed_references",
    "finish_reason",
    "prompt_tokens",
    "completion_tokens",
    "retry_count",
    "attempts",
    "status",
    "runtime_lock_sha256",
    "code_commit",
)


def read(path: Path) -> list[dict[str, object]]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line]


def main() -> None:
    if len(sys.argv) != 5:
        raise SystemExit(
            "usage: verify_generation_compatibility.py QWEN_A QWEN_B MISTRAL_A MISTRAL_B"
        )
    commit = subprocess.check_output(["git", "rev-parse", "HEAD"], text=True).strip()
    result: dict[str, object] = {
        "ok": True,
        "code_commit": commit,
    }
    labels = ("qwen", "mistral")
    for pair_index, label in enumerate(labels):
        first_path = Path(sys.argv[1 + pair_index * 2])
        second_path = Path(sys.argv[2 + pair_index * 2])
        first, second = read(first_path), read(second_path)
        if len(first) != 24 or len(second) != 24:
            raise RuntimeError(f"{label} artifacts must each contain 24 records")
        if any(row["code_commit"] != commit for row in [*first, *second]):
            raise RuntimeError(f"{label} artifacts were produced by another commit")
        for index, (left, right) in enumerate(zip(first, second, strict=True)):
            mismatches = [field for field in FIELDS if left[field] != right[field]]
            if mismatches:
                raise RuntimeError(f"{label} record {index} differs in fields: {mismatches}")
        result[label] = {
            "records_per_run": 24,
            "successful_per_run": sum(row["status"] == "ok" for row in first),
            "failed_per_run": sum(row["status"] != "ok" for row in first),
            "retried_per_run": sum(int(row["retry_count"]) for row in first),
            "model_artifact_sha256": first[0]["model_artifact_sha256"],
        }
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
