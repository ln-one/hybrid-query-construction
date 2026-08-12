from __future__ import annotations

import os
import platform
import subprocess
from pathlib import Path


def _major_version(java: Path) -> int | None:
    if not java.exists():
        return None
    output = subprocess.check_output([java, "-version"], stderr=subprocess.STDOUT, text=True)
    first = output.splitlines()[0]
    token = first.split('"')[1].split(".")[0]
    return int(token)


def ensure_java_runtime(required_major: int) -> Path:
    candidates: list[Path] = []
    if os.environ.get("JAVA_HOME"):
        candidates.append(Path(os.environ["JAVA_HOME"]))
    if platform.system() == "Darwin":
        candidates.extend(
            [
                Path(
                    f"/opt/homebrew/opt/openjdk@{required_major}/libexec/openjdk.jdk/Contents/Home"
                ),
                Path(
                    f"/usr/local/opt/openjdk@{required_major}/libexec/openjdk.jdk/Contents/Home"
                ),
            ]
        )
        try:
            detected = subprocess.check_output(
                ["/usr/libexec/java_home", "-v", str(required_major)], text=True
            ).strip()
            candidates.append(Path(detected))
        except subprocess.CalledProcessError:
            pass
    candidates.extend(
        [
            Path(f"/usr/lib/jvm/java-{required_major}-openjdk"),
            Path(f"/usr/lib/jvm/java-{required_major}-openjdk-amd64"),
        ]
    )
    for home in candidates:
        java = home / "bin" / "java"
        if _major_version(java) == required_major:
            os.environ["JAVA_HOME"] = str(home)
            os.environ["PATH"] = f"{home / 'bin'}{os.pathsep}{os.environ['PATH']}"
            return home
    raise RuntimeError(
        f"Java {required_major} is required by the frozen Pyserini release and was not found"
    )
