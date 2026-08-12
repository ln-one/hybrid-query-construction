#!/bin/sh
set -eu

repo_root=$(CDPATH= cd -- "$(dirname -- "$0")/.." && pwd)
temporary_root=$(mktemp -d "${TMPDIR:-/tmp}/hqc-clean-rebuild.XXXXXX")
trap 'rm -rf "$temporary_root"' EXIT HUP INT TERM

if [ ! -f "$repo_root/artifacts/lock/pre-heldout-v1.json" ]; then
  echo "missing pre-held-out lock" >&2
  exit 1
fi
if [ ! -f "$repo_root/report/REPORT.md" ]; then
  echo "build the reference report before clean rebuild" >&2
  exit 1
fi

cd "$repo_root"
UV_PROJECT_ENVIRONMENT="$temporary_root/venv" uv sync --frozen --extra dev
UV_PROJECT_ENVIRONMENT="$temporary_root/venv" uv run --frozen hqc verify-lock
UV_PROJECT_ENVIRONMENT="$temporary_root/venv" uv run --frozen hqc report \
  --input artifacts/results/raw --output "$temporary_root/report"

diff -ru "$repo_root/report" "$temporary_root/report"
echo "clean rebuild matches report byte for byte"
