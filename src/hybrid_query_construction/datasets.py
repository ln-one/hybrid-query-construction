from __future__ import annotations

import csv
import io
import json
import zipfile
from collections.abc import Iterator
from pathlib import Path
from typing import Any
from urllib.parse import unquote, urlparse

import requests

from .io import atomic_write_bytes, read_jsonl, sha256_file, write_json


def download_archive(url: str, destination: Path) -> Path:
    if destination.exists():
        return destination
    destination.parent.mkdir(parents=True, exist_ok=True)
    parsed = urlparse(url)
    if parsed.scheme == "file":
        atomic_write_bytes(destination, Path(unquote(parsed.path)).read_bytes())
        return destination
    response = requests.get(url, timeout=120, stream=True)
    response.raise_for_status()
    payload = io.BytesIO()
    for chunk in response.iter_content(1024 * 1024):
        payload.write(chunk)
    atomic_write_bytes(destination, payload.getvalue())
    return destination


def _unique_member(archive: zipfile.ZipFile, suffix: str) -> str:
    matches = [name for name in archive.namelist() if name.endswith(suffix)]
    if len(matches) != 1:
        raise ValueError(f"expected one {suffix!r} member, found {matches}")
    return matches[0]


def prepare_beir_dataset(
    dataset_id: str,
    url: str,
    root: Path,
    *,
    heldout: bool,
    split: str = "test",
) -> dict[str, Any]:
    cache = root / "data" / "cache" / f"{dataset_id}.zip"
    processed = root / "data" / "processed" / dataset_id
    archive_path = download_archive(url, cache)
    with zipfile.ZipFile(archive_path) as archive:
        members = {
            "corpus": _unique_member(archive, "corpus.jsonl"),
            "queries": _unique_member(archive, "queries.jsonl"),
            "qrels": _unique_member(archive, f"qrels/{split}.tsv"),
        }
        for kind in ("corpus", "queries"):
            atomic_write_bytes(processed / f"{kind}.jsonl", archive.read(members[kind]))
        if not heldout:
            atomic_write_bytes(processed / "qrels.tsv", archive.read(members["qrels"]))

    manifest = {
        "schema_version": 1,
        "dataset": dataset_id,
        "source_url": url,
        "split": split,
        "heldout": heldout,
        "license": "see upstream BEIR dataset card",
        "archive_sha256": sha256_file(archive_path),
        "corpus_sha256": sha256_file(processed / "corpus.jsonl"),
        "queries_sha256": sha256_file(processed / "queries.jsonl"),
        "qrels_state": "sealed_in_archive" if heldout else "development_available",
        "qrels_member": members["qrels"],
    }
    write_json(processed / "manifest.json", manifest)
    return manifest


def unseal_qrels(dataset_id: str, root: Path, lock_path: Path) -> Path:
    if not lock_path.exists():
        raise RuntimeError("pre-held-out lock is required before qrels extraction")
    manifest_path = root / "data" / "processed" / dataset_id / "manifest.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    if not manifest["heldout"]:
        raise ValueError(f"{dataset_id} is not held out")
    archive_path = root / "data" / "cache" / f"{dataset_id}.zip"
    destination = root / "data" / "processed" / dataset_id / "qrels.tsv"
    with zipfile.ZipFile(archive_path) as archive:
        atomic_write_bytes(destination, archive.read(manifest["qrels_member"]))
    manifest["qrels_state"] = "unsealed_after_lock"
    manifest["qrels_sha256"] = sha256_file(destination)
    write_json(manifest_path, manifest)
    return destination


def load_queries(path: Path) -> dict[str, str]:
    queries: dict[str, str] = {}
    for row in read_jsonl(path):
        query_id = str(row.get("_id", row.get("id")))
        queries[query_id] = str(row["text"])
    return queries


def iter_corpus(path: Path) -> Iterator[tuple[str, str]]:
    for row in read_jsonl(path):
        document_id = str(row.get("_id", row.get("id")))
        title = str(row.get("title", "")).strip()
        text = str(row.get("text", row.get("contents", ""))).strip()
        yield document_id, "\n".join(part for part in (title, text) if part)


def load_qrels(path: Path) -> dict[str, dict[str, int]]:
    qrels: dict[str, dict[str, int]] = {}
    with path.open(encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle, delimiter="\t")
        for row in reader:
            query_id = str(row.get("query-id", row.get("query_id")))
            document_id = str(row.get("corpus-id", row.get("doc_id")))
            score = int(row["score"])
            qrels.setdefault(query_id, {})[document_id] = score
    return qrels
