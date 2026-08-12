from __future__ import annotations

import platform
import subprocess
import sys
from pathlib import Path

import torch

from .generation import current_commit
from .io import sha256_file, write_json
from .java import ensure_java_runtime


def capture_environment(root: Path, output: Path, java_major: int = 21) -> dict[str, object]:
    ensure_java_runtime(java_major)
    java = subprocess.check_output(["java", "-version"], stderr=subprocess.STDOUT, text=True)
    packages = subprocess.check_output(
        ["uv", "pip", "freeze", "--strict"], cwd=root, text=True
    ).splitlines()
    packages = [
        "hybrid-query-construction==editable-local" if line.startswith("-e file:") else line
        for line in packages
    ]
    manifest: dict[str, object] = {
        "schema_version": 1,
        "protocol_version": "hqc-formal-v1",
        "platform": platform.platform(),
        "machine": platform.machine(),
        "processor": platform.processor(),
        "python": sys.version,
        "java": java.strip(),
        "torch": torch.__version__,
        "mps_available": torch.backends.mps.is_available(),
        "mps_built": torch.backends.mps.is_built(),
        "packages": packages,
        "uv_lock_sha256": sha256_file(root / "uv.lock"),
        "code_commit": current_commit(root),
    }
    write_json(output, manifest)
    return manifest
