from __future__ import annotations

import csv
import hashlib
import io
import json
import zipfile
from collections.abc import Iterator
from pathlib import Path
from typing import Any
from urllib.parse import unquote, urlparse

import requests

from .io import atomic_write_bytes, atomic_write_text, read_jsonl, sha256_file, write_json


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
        atomic_write_bytes(processed / "corpus.jsonl", archive.read(members["corpus"]))
        qrels_text = archive.read(members["qrels"]).decode("utf-8")
        qrels_reader = csv.DictReader(io.StringIO(qrels_text), delimiter="\t")
        evaluation_query_ids = {
            str(row.get("query-id", row.get("query_id"))) for row in qrels_reader
        }
        query_rows = [
            row
            for row in (
                json.loads(line)
                for line in archive.read(members["queries"]).decode("utf-8").splitlines()
                if line.strip()
            )
            if str(row.get("_id", row.get("id"))) in evaluation_query_ids
        ]
        selected_query_ids = {str(row.get("_id", row.get("id"))) for row in query_rows}
        if selected_query_ids != evaluation_query_ids:
            missing = evaluation_query_ids - selected_query_ids
            raise RuntimeError(f"split queries absent from queries.jsonl: {len(missing)}")
        atomic_write_text(
            processed / "queries.jsonl",
            "".join(json.dumps(row, ensure_ascii=False) + "\n" for row in query_rows),
        )
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
        "evaluation_query_count": len(evaluation_query_ids),
        "query_selection": "query_ids_present_in_selected_qrels_split_without_labels",
        "qrels_state": "sealed_in_archive" if heldout else "development_available",
        "qrels_member": members["qrels"],
    }
    write_json(processed / "manifest.json", manifest)
    return manifest


def unseal_qrels(dataset_id: str, root: Path, lock_path: Path) -> Path:
    if not lock_path.exists():
        raise RuntimeError("pre-held-out lock is required before qrels extraction")
    from .locking import verify_lock

    verify_lock(root, lock_path)
    manifest_path = root / "data" / "processed" / dataset_id / "manifest.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    if not manifest["heldout"]:
        raise ValueError(f"{dataset_id} is not held out")
    archive_path = root / "data" / "cache" / f"{dataset_id}.zip"
    destination = root / "data" / "processed" / dataset_id / "qrels.tsv"
    with zipfile.ZipFile(archive_path) as archive:
        atomic_write_bytes(destination, archive.read(manifest["qrels_member"]))
    write_json(
        root / "artifacts" / "lock" / f"unsealed-{dataset_id}.json",
        {
            "schema_version": 1,
            "dataset": dataset_id,
            "qrels_sha256": sha256_file(destination),
            "preheldout_lock_sha256": sha256_file(lock_path),
        },
    )
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


def prepare_nested_snapshots(
    dataset_id: str,
    root: Path,
    sizes: list[int],
) -> list[dict[str, Any]]:
    """Create deterministic nested corpora while retaining every relevant document."""
    source = root / "data" / "processed" / dataset_id
    corpus_rows = list(read_jsonl(source / "corpus.jsonl"))
    qrels = load_qrels(source / "qrels.tsv")
    relevant = {
        document_id
        for judgments in qrels.values()
        for document_id, grade in judgments.items()
        if grade > 0
    }
    by_id = {str(row.get("_id", row.get("id"))): row for row in corpus_rows}
    missing = relevant - by_id.keys()
    if missing:
        raise RuntimeError(f"relevant documents absent from corpus: {len(missing)}")
    ordered_remainder = sorted(
        by_id.keys() - relevant,
        key=lambda document_id: (
            hashlib.sha256(document_id.encode()).hexdigest(),
            document_id,
        ),
    )
    manifests: list[dict[str, Any]] = []
    previous: set[str] = set()
    for requested_size in sorted(set(sizes)):
        if requested_size < len(relevant):
            message = (
                f"snapshot size {requested_size} cannot retain "
                f"{len(relevant)} relevant documents"
            )
            raise ValueError(message)
        actual_size = min(requested_size, len(by_id))
        selected = relevant | set(ordered_remainder[: actual_size - len(relevant)])
        if previous and not previous <= selected:
            raise AssertionError("snapshot selection is not nested")
        previous = selected
        destination = root / "data" / "processed" / f"{dataset_id}-{actual_size}"
        rows = [by_id[document_id] for document_id in sorted(selected)]
        atomic_write_text(
            destination / "corpus.jsonl",
            "".join(json.dumps(row, ensure_ascii=False) + "\n" for row in rows),
        )
        atomic_write_bytes(
            destination / "queries.jsonl", (source / "queries.jsonl").read_bytes()
        )
        atomic_write_bytes(destination / "qrels.tsv", (source / "qrels.tsv").read_bytes())
        manifest = {
            "schema_version": 1,
            "source_dataset": dataset_id,
            "dataset": f"{dataset_id}-{actual_size}",
            "requested_size": requested_size,
            "actual_size": actual_size,
            "relevant_documents_retained": len(relevant),
            "selection": "all_relevant_then_sha256_docid_ascending",
            "corpus_sha256": sha256_file(destination / "corpus.jsonl"),
            "queries_sha256": sha256_file(destination / "queries.jsonl"),
            "qrels_sha256": sha256_file(destination / "qrels.tsv"),
        }
        write_json(destination / "manifest.json", manifest)
        manifests.append(manifest)
    return manifests
