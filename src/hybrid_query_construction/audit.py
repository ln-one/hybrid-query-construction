from __future__ import annotations

import json
import sqlite3
import subprocess
from collections import Counter
from functools import cache
from pathlib import Path
from typing import Any

from .datasets import load_queries
from .generation import current_commit
from .io import hash_selected, read_jsonl, sha256_file, stable_seed
from .model_conversion import verify_model_artifact
from .models import GenerationRecord
from .storage import ranking_store_digest

DEVELOPMENT = ("scifact", "nfcorpus", "trec-covid")
HELDOUT = ("fiqa", "arguana", "webis-touche2020", "scidocs")
ALL_DATASETS = DEVELOPMENT + HELDOUT
SCALES = (
    "trec-covid-25000",
    "trec-covid-50000",
    "trec-covid-100000",
    "trec-covid-171332",
)
CONTROLLED_CHANNELS = (
    "dense_contextual",
    "dense_residual",
    "sparse_rewrite",
    "sparse_anchor",
    "sparse_mask",
    "sparse_references_only",
    "sparse_mugi",
)


@cache
def _is_ancestor(root: Path, candidate: str, head: str) -> bool:
    if not candidate:
        return False
    result = subprocess.run(
        ["git", "merge-base", "--is-ancestor", candidate, head],
        cwd=root,
        check=False,
        capture_output=True,
    )
    return result.returncode == 0


def _expected_generation_jobs(root: Path) -> list[dict[str, Any]]:
    jobs: list[dict[str, Any]] = []
    for dataset in ALL_DATASETS:
        queries = load_queries(root / "data" / "processed" / dataset / "queries.jsonl")
        for family, count in (("bridge", 5), ("mugi", 5), ("query2doc", 1), ("hyde", 8)):
            if family == "bridge":
                prompt = "prompts/primary-reference-v1.txt"
            elif family == "hyde":
                prompt = {
                    "fiqa": "prompts/baselines/hyde-fiqa-v1.txt",
                    "arguana": "prompts/baselines/hyde-arguana-v1.txt",
                    "scifact": "prompts/baselines/hyde-scifact-v1.txt",
                    "trec-covid": "prompts/baselines/hyde-trec-covid-v1.txt",
                }.get(dataset, "prompts/baselines/hyde-v1.txt")
            else:
                prompt = f"prompts/baselines/{family}-v1.txt"
            jobs.append(
                {
                    "family": family,
                    "dataset": dataset,
                    "path": root / "artifacts" / "generations" / family / f"{dataset}.jsonl",
                    "reference_count": count,
                    "queries": queries,
                    "model_id": "Qwen/Qwen2.5-7B-Instruct",
                    "model_revision": "fe11104b620d588ccc049ff6631dd3ea002e3d98",
                    "prompt_path": prompt,
                    "max_new_tokens": 512 if family == "hyde" else 256,
                    "decoding": {
                        "do_sample": True,
                        "temperature": 0.7,
                        "top_p": 0.9,
                        "top_k": 20,
                        "repetition_penalty": 1.0,
                        "max_new_tokens": 512 if family == "hyde" else 256,
                        "stop_sequence": "]",
                    },
                    "backend": "mlx_lm",
                    "backend_version": "0.31.2",
                    "structured_output_backend": "xgrammar",
                    "structured_output_backend_version": "0.2.1",
                    "query_batch_size": 8,
                    "local_model_path": "data/cache/models/qwen2.5-7b-instruct-mlx-bf16",
                }
            )
    for dataset in HELDOUT:
        queries = load_queries(root / "data" / "processed" / dataset / "queries.jsonl")
        jobs.append(
            {
                "family": "robustness",
                "dataset": dataset,
                "path": root / "artifacts" / "generations" / "robustness" / f"{dataset}.jsonl",
                "reference_count": 5,
                "queries": {key: queries[key] for key in hash_selected(queries, 100)},
                "model_id": "mistralai/Mistral-7B-Instruct-v0.3",
                "model_revision": "c170c708c41dac9275d15a8fff4eca08d52bab71",
                "prompt_path": "prompts/primary-reference-v1.txt",
                "max_new_tokens": 256,
                "decoding": {
                    "do_sample": True,
                    "temperature": 0.7,
                    "top_p": 0.9,
                    "top_k": 20,
                    "repetition_penalty": 1.0,
                    "max_new_tokens": 256,
                    "stop_sequence": "]",
                },
                "backend": "mlx_lm",
                "backend_version": "0.31.2",
                "structured_output_backend": "xgrammar",
                "structured_output_backend_version": "0.2.1",
                "query_batch_size": 8,
                "local_model_path": "data/cache/models/mistral-7b-instruct-v0.3-mlx-bf16",
            }
        )
    return jobs


def _audit_generation_job(
    root: Path,
    job: dict[str, Any],
    expected_commit: str,
    runtime_hash: str,
    model_artifact_sha256: str,
    model_artifact_error: str | None,
) -> dict[str, Any]:
    path = Path(job["path"])
    queries = job["queries"]
    expected_pairs = {(query_id, draw_id) for query_id in queries for draw_id in range(3)}
    prompt_path = root / job["prompt_path"]
    prompt_hash = sha256_file(prompt_path)
    errors: list[str] = []
    if model_artifact_error is not None:
        errors.append(f"invalid converted model artifact: {model_artifact_error}")
    ordered_query_ids = sorted(queries)
    batch_by_query = {
        query_id: index // int(job["query_batch_size"])
        for index, query_id in enumerate(ordered_query_ids)
    }
    records: list[GenerationRecord] = []
    if path.exists():
        try:
            records = [GenerationRecord.model_validate(row) for row in read_jsonl(path)]
        except Exception as error:
            errors.append(f"invalid JSONL: {error}")
    else:
        errors.append("missing file")
    actual_pairs = [(record.query_id, record.draw_id) for record in records]
    duplicates = [pair for pair, count in Counter(actual_pairs).items() if count > 1]
    if duplicates:
        errors.append(f"duplicate query/draw pairs: {duplicates[:3]}")
    actual_pair_set = set(actual_pairs)
    missing = expected_pairs - actual_pair_set
    unexpected = actual_pair_set - expected_pairs
    if missing:
        errors.append(f"missing {len(missing)} query/draw pairs")
    if unexpected:
        errors.append(f"unexpected {len(unexpected)} query/draw pairs")
    for record in records:
        if record.dataset != job["dataset"]:
            errors.append(f"dataset mismatch for {record.query_id}/{record.draw_id}")
        if record.model_id != job["model_id"]:
            errors.append(f"model mismatch for {record.query_id}/{record.draw_id}")
        if record.model_revision != job["model_revision"]:
            errors.append(f"model revision mismatch for {record.query_id}/{record.draw_id}")
        if record.tokenizer_revision != job["model_revision"]:
            errors.append(f"tokenizer revision mismatch for {record.query_id}/{record.draw_id}")
        if record.backend != job["backend"]:
            errors.append(f"backend mismatch for {record.query_id}/{record.draw_id}")
        if record.backend_version != job["backend_version"]:
            errors.append(f"backend version mismatch for {record.query_id}/{record.draw_id}")
        if record.structured_output_backend != job["structured_output_backend"]:
            errors.append(f"structured backend mismatch for {record.query_id}/{record.draw_id}")
        if record.structured_output_backend_version != job["structured_output_backend_version"]:
            errors.append(
                f"structured backend version mismatch for {record.query_id}/{record.draw_id}"
            )
        if record.model_artifact_sha256 != model_artifact_sha256:
            errors.append(f"model artifact mismatch for {record.query_id}/{record.draw_id}")
        if record.prompt_path != job["prompt_path"] or record.prompt_sha256 != prompt_hash:
            errors.append(f"prompt mismatch for {record.query_id}/{record.draw_id}")
        if record.decoding.model_dump() != job["decoding"]:
            errors.append(f"decoding mismatch for {record.query_id}/{record.draw_id}")
        if not _is_ancestor(root, record.code_commit, expected_commit):
            errors.append(f"commit mismatch for {record.query_id}/{record.draw_id}")
        if record.runtime_lock_sha256 != runtime_hash:
            errors.append(f"runtime lock mismatch for {record.query_id}/{record.draw_id}")
        expected_count = int(job["reference_count"])
        if record.status == "ok" and len(record.parsed_references) != expected_count:
            errors.append(f"reference count mismatch for {record.query_id}/{record.draw_id}")
        if record.status == "ok" and record.attempts[-1].parse_error is not None:
            errors.append(
                f"successful record has parse error for {record.query_id}/{record.draw_id}"
            )
        if record.status == "generation_failed" and record.parsed_references:
            errors.append(
                f"failed record has parsed references for {record.query_id}/{record.draw_id}"
            )
        if record.status == "generation_failed" and record.attempts[-1].parse_error is None:
            errors.append(
                f"failed record lacks parse error for {record.query_id}/{record.draw_id}"
            )
        if record.query_id in queries and record.query_text != queries[record.query_id]:
            errors.append(f"query text mismatch for {record.query_id}/{record.draw_id}")
        expected_seed = stable_seed(
            "hqc-formal-v1",
            job["dataset"],
            prompt_hash,
            str(batch_by_query.get(record.query_id, -1)),
        )
        if record.seed != expected_seed:
            errors.append(f"seed mismatch for {record.query_id}/{record.draw_id}")
    return {
        "family": job["family"],
        "dataset": job["dataset"],
        "path": str(path),
        "expected": len(expected_pairs),
        "actual": len(records),
        "complete": not errors,
        "errors": sorted(set(errors)),
    }


def _expected_ranking_keys(
    all_queries: set[str], controlled_queries: set[str], include_fidelity: bool
) -> set[tuple[str, int, str, str, int]]:
    expected = {
        (query_id, 0, "base", channel, 0)
        for query_id in all_queries
        for channel in ("dense_original", "sparse_original")
    }
    expected.update(
        (query_id, draw_id, "controlled", channel, reference_count)
        for query_id in controlled_queries
        for draw_id in range(3)
        for reference_count in (1, 3, 5)
        for channel in CONTROLLED_CHANNELS
    )
    if include_fidelity:
        for method, reference_count in (("mugi", 5), ("hyde", 8), ("query2doc", 1)):
            expected.update(
                (query_id, draw_id, "fidelity", channel, reference_count)
                for query_id in all_queries
                for draw_id in range(3)
                for channel in (f"dense_{method}", f"sparse_{method}")
            )
    return expected


def _read_ranking_keys(path: Path, dataset: str) -> set[tuple[str, int, str, str, int]]:
    connection = sqlite3.connect(path)
    try:
        return {
            (str(query_id), int(draw_id), str(track), str(channel), int(reference_count))
            for query_id, draw_id, track, channel, reference_count in connection.execute(
                """SELECT query_id, draw_id, track, channel, reference_count
                FROM rankings WHERE dataset=?""",
                (dataset,),
            )
        }
    finally:
        connection.close()


def _ranking_reuse_errors(
    root: Path,
    store: Path,
    spec_value: dict[str, Any],
    manifest_value: dict[str, Any],
) -> list[str]:
    reuse = spec_value.get("ranking_reuse")
    if reuse is None:
        return []
    errors: list[str] = []
    source = root / str(reuse["source"])
    if not source.exists():
        return ["ranking reuse source is missing"]
    if ranking_store_digest(source) != reuse.get("source_store_sha256"):
        errors.append("ranking reuse source hash mismatch")
    mode = str(reuse.get("mode"))
    predicate = (
        "source.track='base'"
        if mode == "base"
        else "source.channel LIKE 'sparse_%' AND source.track!='fidelity'"
    )
    if mode not in {"base", "sparse"}:
        return [f"unsupported ranking reuse mode in specification: {mode}"]
    connection = sqlite3.connect(store)
    try:
        connection.execute("ATTACH DATABASE ? AS reused_source", (str(source),))
        source_documents = connection.execute(
            "SELECT value FROM reused_source.metadata WHERE key='documents_sha256'"
        ).fetchone()
        target_documents = connection.execute(
            "SELECT value FROM metadata WHERE key='documents_sha256'"
        ).fetchone()
        if source_documents != target_documents:
            errors.append("ranking reuse document collection mismatch")
        selected = int(
            connection.execute(
                f"SELECT COUNT(*) FROM reused_source.rankings AS source WHERE {predicate}"
            ).fetchone()[0]
        )
        mismatches = int(
            connection.execute(
                f"""SELECT COUNT(*) FROM reused_source.rankings AS source
                LEFT JOIN rankings AS target
                ON target.dataset=source.dataset AND target.query_id=source.query_id
                AND target.draw_id=source.draw_id AND target.track=source.track
                AND target.channel=source.channel
                AND target.reference_count=source.reference_count
                WHERE {predicate} AND (
                    target.ranking_sha256 IS NULL
                    OR target.ranking_sha256!=source.ranking_sha256
                    OR target.support!=source.support
                    OR target.fallback!=source.fallback
                    OR target.generation_sha256!=source.generation_sha256
                )"""
            ).fetchone()[0]
        )
    finally:
        connection.close()
    evidence = manifest_value.get("reuse_evidence") or {}
    if int(evidence.get("selected", -1)) != selected:
        errors.append("ranking reuse evidence count mismatch")
    if int(evidence.get("ordinal_rows_verified", -1)) != selected:
        errors.append("ranking reuse ordinal verification incomplete")
    if mismatches:
        errors.append(f"ranking reuse parity mismatch for {mismatches} rows")
    return errors


def _audit_ranking_job(
    *,
    root: Path,
    dataset: str,
    run_id: str,
    controlled_queries: set[str],
    include_fidelity: bool,
    expected_commit: str,
) -> dict[str, Any]:
    directory = root / "artifacts" / "rankings" / dataset
    store_name = "rankings.sqlite3" if run_id == "primary" else f"rankings-{run_id}.sqlite3"
    spec_name = "rankings-spec.json" if run_id == "primary" else f"rankings-{run_id}-spec.json"
    manifest_name = (
        "rankings-manifest.json" if run_id == "primary" else f"rankings-{run_id}-manifest.json"
    )
    store = directory / store_name
    spec = directory / spec_name
    manifest = directory / manifest_name
    errors: list[str] = []
    all_queries = set(load_queries(root / "data" / "processed" / dataset / "queries.jsonl"))
    expected = _expected_ranking_keys(all_queries, controlled_queries, include_fidelity)
    actual: set[tuple[str, int, str, str, int]] = set()
    if not store.exists():
        errors.append("missing ranking store")
    else:
        try:
            actual = _read_ranking_keys(store, dataset)
        except Exception as error:
            errors.append(f"unreadable ranking store: {error}")
    spec_value: dict[str, Any] = {}
    if not spec.exists():
        errors.append("missing ranking specification")
    else:
        spec_value = json.loads(spec.read_text(encoding="utf-8"))
        if not _is_ancestor(root, str(spec_value.get("code_commit", "")), expected_commit):
            errors.append("ranking specification commit mismatch")
    manifest_value: dict[str, Any] = {}
    if not manifest.exists():
        errors.append("missing ranking manifest")
    elif store.exists():
        manifest_value = json.loads(manifest.read_text(encoding="utf-8"))
        if manifest_value.get("ranking_store_sha256") != ranking_store_digest(store):
            errors.append("ranking store hash mismatch")
    if store.exists() and spec_value and manifest_value:
        errors.extend(_ranking_reuse_errors(root, store, spec_value, manifest_value))
    missing = expected - actual
    unexpected = actual - expected
    if missing:
        errors.append(f"missing {len(missing)} ranking keys")
    if unexpected:
        errors.append(f"unexpected {len(unexpected)} ranking keys")
    return {
        "dataset": dataset,
        "run_id": run_id,
        "expected": len(expected),
        "actual": len(actual),
        "complete": not errors,
        "errors": errors,
    }


def ranking_progress(root: Path, dataset: str, run_id: str) -> dict[str, Any]:
    query_ids = set(load_queries(root / "data" / "processed" / dataset / "queries.jsonl"))
    controlled_queries = (
        set(hash_selected(query_ids, 100)) if run_id == "mistral" else query_ids
    )
    result = _audit_ranking_job(
        root=root,
        dataset=dataset,
        run_id=run_id,
        controlled_queries=controlled_queries,
        include_fidelity=run_id == "primary" and dataset in ALL_DATASETS,
        expected_commit=current_commit(root),
    )
    if not result["complete"]:
        raise RuntimeError(
            f"ranking artifact is incomplete for {dataset}/{run_id}: {result['errors']}"
        )
    return result


def generation_progress(root: Path, group: str) -> dict[str, Any]:
    if group not in {"qwen", "robustness"}:
        raise ValueError(f"unsupported generation group: {group}")
    jobs = [
        job
        for job in _expected_generation_jobs(root)
        if (job["family"] == "robustness") == (group == "robustness")
    ]
    commit = current_commit(root)
    runtime_hash = sha256_file(root / "uv.lock")
    model_artifacts: dict[str, tuple[str, str | None]] = {}
    for job in jobs:
        local_path = str(job["local_model_path"])
        if local_path in model_artifacts:
            continue
        try:
            manifest = verify_model_artifact(root / local_path)
            model_artifacts[local_path] = (str(manifest["artifact_sha256"]), None)
        except Exception as error:
            model_artifacts[local_path] = ("", str(error))
    results = [
        _audit_generation_job(
            root,
            job,
            commit,
            runtime_hash,
            *model_artifacts[str(job["local_model_path"])],
        )
        for job in jobs
    ]
    complete = all(result["complete"] for result in results)
    summary = {
        "group": group,
        "complete": complete,
        "actual": sum(int(result["actual"]) for result in results),
        "expected": sum(int(result["expected"]) for result in results),
        "jobs": results,
    }
    if not complete:
        incomplete = [
            f"{result['family']}:{result['dataset']}"
            for result in results
            if not result["complete"]
        ]
        raise RuntimeError(f"generation artifacts incomplete: {incomplete}")
    return summary


def formal_progress(root: Path, *, require_complete: bool = False) -> dict[str, Any]:
    commit = current_commit(root)
    runtime_hash = sha256_file(root / "uv.lock")
    jobs = _expected_generation_jobs(root)
    model_artifacts: dict[str, tuple[str, str | None]] = {}
    for job in jobs:
        local_path = str(job["local_model_path"])
        if local_path in model_artifacts:
            continue
        try:
            manifest = verify_model_artifact(root / local_path)
            expected = (
                job["model_id"],
                job["model_revision"],
                "bfloat16",
                job["backend"],
                job["backend_version"],
                False,
            )
            actual = (
                manifest.get("model_id"),
                manifest.get("source_revision"),
                manifest.get("dtype"),
                manifest.get("backend"),
                manifest.get("backend_version"),
                manifest.get("quantized"),
            )
            if actual != expected:
                raise RuntimeError(f"model manifest mismatch: {actual} != {expected}")
            model_artifacts[local_path] = (str(manifest["artifact_sha256"]), None)
        except Exception as error:
            model_artifacts[local_path] = ("", str(error))
    generations = [
        _audit_generation_job(
            root,
            job,
            commit,
            runtime_hash,
            *model_artifacts[str(job["local_model_path"])],
        )
        for job in jobs
    ]
    rankings: list[dict[str, Any]] = []
    for dataset in ALL_DATASETS:
        query_ids = set(load_queries(root / "data" / "processed" / dataset / "queries.jsonl"))
        rankings.append(
            _audit_ranking_job(
                root=root,
                dataset=dataset,
                run_id="primary",
                controlled_queries=query_ids,
                include_fidelity=True,
                expected_commit=commit,
            )
        )
    for dataset in HELDOUT:
        query_ids = set(load_queries(root / "data" / "processed" / dataset / "queries.jsonl"))
        rankings.append(
            _audit_ranking_job(
                root=root,
                dataset=dataset,
                run_id="mistral",
                controlled_queries=set(hash_selected(query_ids, 100)),
                include_fidelity=False,
                expected_commit=commit,
            )
        )
        rankings.append(
            _audit_ranking_job(
                root=root,
                dataset=dataset,
                run_id="contriever",
                controlled_queries=query_ids,
                include_fidelity=False,
                expected_commit=commit,
            )
        )
    for dataset in SCALES:
        query_ids = set(load_queries(root / "data" / "processed" / dataset / "queries.jsonl"))
        rankings.append(
            _audit_ranking_job(
                root=root,
                dataset=dataset,
                run_id="primary",
                controlled_queries=query_ids,
                include_fidelity=False,
                expected_commit=commit,
            )
        )
    complete = all(item["complete"] for item in [*generations, *rankings])
    result = {
        "schema_version": 1,
        "protocol_version": "hqc-formal-v1",
        "code_commit": commit,
        "complete": complete,
        "generation_records": {
            "actual": sum(int(item["actual"]) for item in generations),
            "expected": sum(int(item["expected"]) for item in generations),
        },
        "ranking_keys": {
            "actual": sum(int(item["actual"]) for item in rankings),
            "expected": sum(int(item["expected"]) for item in rankings),
        },
        "generations": generations,
        "rankings": rankings,
    }
    if require_complete and not complete:
        incomplete = [
            f"{item.get('family', item.get('run_id'))}:{item['dataset']}"
            for item in [*generations, *rankings]
            if not item["complete"]
        ]
        raise RuntimeError(f"formal pre-evaluation artifacts incomplete: {incomplete}")
    return result
