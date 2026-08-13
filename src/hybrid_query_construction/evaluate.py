from __future__ import annotations

from collections.abc import Iterable
from pathlib import Path

from .datasets import load_qrels
from .fusion import complete_wrrf, fixed_top_l_wrrf
from .io import canonical_json, sha256_bytes, sha256_file, write_json
from .metrics import ndcg_at_k, recall_at_k
from .models import QueryResult
from .replay import replay_complete_wrrf
from .storage import RankingArtifact, RankingStore

CONTROLLED_METHODS = {
    "original": ("base:dense_original", "base:sparse_original"),
    "bridge_shared": ("controlled:dense_contextual", "controlled:sparse_rewrite"),
    "dense_only": ("controlled:dense_residual", "base:sparse_original"),
    "sparse_only": ("base:dense_original", "controlled:sparse_anchor"),
    "mugi_controlled": ("controlled:dense_contextual", "controlled:sparse_mugi"),
    "proposed": ("controlled:dense_residual", "controlled:sparse_anchor"),
    "sparse_boolean_mask": ("controlled:dense_residual", "controlled:sparse_mask"),
    "sparse_references_only": (
        "controlled:dense_residual",
        "controlled:sparse_references_only",
    ),
}

FIDELITY_METHODS = {
    "mugi": ("fidelity:dense_mugi", "fidelity:sparse_mugi"),
    "hyde": ("fidelity:dense_hyde", "fidelity:sparse_hyde"),
    "query2doc": ("fidelity:dense_query2doc", "fidelity:sparse_query2doc"),
}


def _artifact(
    store: RankingStore,
    spec: str,
    *,
    query_id: str,
    draw_id: int,
    reference_count: int,
) -> RankingArtifact:
    track, channel = spec.split(":", maxsplit=1)
    if track == "base":
        return store.get(
            query_id=query_id,
            draw_id=0,
            track="base",
            channel=channel,
            reference_count=0,
        )
    return store.get(
        query_id=query_id,
        draw_id=draw_id,
        track=track,
        channel=channel,
        reference_count=reference_count,
    )


def _result(
    *,
    dataset: str,
    query_id: str,
    draw_id: int,
    track: str,
    condition_id: str,
    method: str,
    reference_count: int,
    dense: RankingArtifact,
    sparse: RankingArtifact,
    qrels: dict[str, int],
    top_k: int,
    constant: int,
    method_config_sha256: str,
) -> QueryResult:
    fused = complete_wrrf((dense.ranking, sparse.ranking), top_k=top_k, constant=constant)
    replay = replay_complete_wrrf(
        dense.ranking, sparse.ranking, top_k=top_k, constant=constant, keep_trace=True
    )
    if list(replay.ordered_top_k) != fused:
        raise AssertionError("replay result does not match complete fusion")
    trace_sha = sha256_bytes(canonical_json(replay.trace).encode())
    generation_sha = sha256_bytes(
        f"{dense.generation_sha256}\x1f{sparse.generation_sha256}".encode()
    )
    return QueryResult(
        protocol_version="hqc-formal-v1",
        dataset=dataset,
        query_id=query_id,
        draw_id=draw_id,
        track=track,
        condition_id=condition_id,
        method=method,
        reference_count=reference_count,
        rrf_constant=constant,
        ndcg_at_10=ndcg_at_k(fused, qrels, 10),
        recall_at_20=recall_at_k(fused, qrels, 20),
        dense_depth=replay.dense_depth,
        sparse_depth=replay.sparse_depth,
        sparse_support=sparse.support,
        sparse_exhausted=replay.sparse_exhausted,
        ordered_top20=tuple(fused),
        generation_artifact_sha256=generation_sha,
        dense_ranking_sha256=dense.ranking_sha256,
        sparse_ranking_sha256=sparse.ranking_sha256,
        method_config_sha256=method_config_sha256,
        replay_trace_sha256=trace_sha,
        fallback=dense.fallback or sparse.fallback,
    )


def _write_jsonl(path: Path, rows: Iterable[dict[str, object]]) -> None:
    payload = "".join(canonical_json(row) + "\n" for row in rows)
    from .io import atomic_write_text

    atomic_write_text(path, payload)


def evaluate_rankings(
    *,
    root: Path,
    dataset: str,
    store_path: Path,
    output_directory: Path,
    reference_count: int = 5,
    top_k: int = 20,
    constant: int = 60,
    fixed_top_l: tuple[int, ...] = (10, 20, 50, 100, 200, 500, 1000),
    result_track: str | None = None,
    condition_id: str = "primary",
    include_fidelity: bool = True,
    output_id: str | None = None,
) -> tuple[Path, Path]:
    qrels_path = root / "data" / "processed" / dataset / "qrels.tsv"
    if not qrels_path.exists():
        raise RuntimeError(f"qrels remain sealed or unavailable: {qrels_path}")
    qrels = load_qrels(qrels_path)
    document_ids = RankingStore.load_document_ids(store_path)
    method_config_sha = sha256_file(root / "configs" / "methods" / "formal-v1.yaml")
    rows: list[QueryResult] = []
    fixed_rows: list[dict[str, object]] = []

    if result_track is None:
        result_track = "controlled" if reference_count == 5 and constant == 60 else "ablation"
    if result_track not in {"controlled", "ablation", "robustness", "scale"}:
        raise ValueError(f"unsupported result track: {result_track}")

    with RankingStore(store_path, dataset, document_ids) as store:
        controlled_keys = list(store.keys())
        controlled_draws = sorted(
            {
                (query_id, draw_id)
                for query_id, draw_id, track, channel, count in controlled_keys
                if track == "controlled"
                and channel == "dense_residual"
                and count == reference_count
                and query_id in qrels
            }
        )
        for query_id, draw_id in controlled_draws:
            for method, (dense_spec, sparse_spec) in CONTROLLED_METHODS.items():
                dense = _artifact(
                    store,
                    dense_spec,
                    query_id=query_id,
                    draw_id=draw_id,
                    reference_count=reference_count,
                )
                sparse = _artifact(
                    store,
                    sparse_spec,
                    query_id=query_id,
                    draw_id=draw_id,
                    reference_count=reference_count,
                )
                result = _result(
                    dataset=dataset,
                    query_id=query_id,
                    draw_id=draw_id,
                    track=result_track,
                    condition_id=condition_id,
                    method=method,
                    reference_count=reference_count,
                    dense=dense,
                    sparse=sparse,
                    qrels=qrels[query_id],
                    top_k=top_k,
                    constant=constant,
                    method_config_sha256=method_config_sha,
                )
                rows.append(result)
                for top_l in fixed_top_l:
                    ranking = fixed_top_l_wrrf(
                        (dense.ranking, sparse.ranking),
                        top_l,
                        top_k=top_k,
                        constant=constant,
                    )
                    fixed_rows.append(
                        {
                            "schema_version": "1.0",
                            "protocol_version": "hqc-formal-v1",
                            "dataset": dataset,
                            "query_id": query_id,
                            "draw_id": draw_id,
                            "track": result_track,
                            "condition_id": condition_id,
                            "method": method,
                            "reference_count": reference_count,
                            "rrf_constant": constant,
                            "top_l": top_l,
                            "ndcg_at_10": ndcg_at_k(ranking, qrels[query_id], 10),
                            "recall_at_20": recall_at_k(ranking, qrels[query_id], 20),
                            "complete_top20_exact": ranking == list(result.ordered_top20),
                        }
                    )

        fidelity_keys = list(store.keys())
        for method, (dense_spec, sparse_spec) in (
            FIDELITY_METHODS.items() if include_fidelity else ()
        ):
            dense_channel = dense_spec.split(":", maxsplit=1)[1]
            method_keys = [
                (query_id, draw_id, count)
                for query_id, draw_id, track, channel, count in fidelity_keys
                if track == "fidelity" and channel == dense_channel and query_id in qrels
            ]
            for query_id, draw_id, count in sorted(method_keys):
                dense = _artifact(
                    store,
                    dense_spec,
                    query_id=query_id,
                    draw_id=draw_id,
                    reference_count=count,
                )
                sparse = _artifact(
                    store,
                    sparse_spec,
                    query_id=query_id,
                    draw_id=draw_id,
                    reference_count=count,
                )
                rows.append(
                    _result(
                        dataset=dataset,
                        query_id=query_id,
                        draw_id=draw_id,
                        track="fidelity",
                        condition_id=condition_id,
                        method=method,
                        reference_count=count,
                        dense=dense,
                        sparse=sparse,
                        qrels=qrels[query_id],
                        top_k=top_k,
                        constant=constant,
                        method_config_sha256=method_config_sha,
                    )
                )

    output_directory.mkdir(parents=True, exist_ok=True)
    if output_id is None:
        output_id = (
            dataset
            if result_track == "controlled" and reference_count == 5 and constant == 60
            else f"{dataset}-{store_path.stem}-{result_track}-r{reference_count}-c{constant}"
        )
    results_path = output_directory / f"{output_id}.jsonl"
    fixed_path = output_directory / f"{output_id}-fixed-top-l.jsonl"
    _write_jsonl(results_path, (row.model_dump(mode="json") for row in rows))
    _write_jsonl(fixed_path, fixed_rows)
    manifest = {
        "schema_version": 1,
        "protocol_version": "hqc-formal-v1",
        "dataset": dataset,
        "output_id": output_id,
        "result_track": result_track,
        "condition_id": condition_id,
        "reference_count": reference_count,
        "rrf_constant": constant,
        "top_k": top_k,
        "fixed_top_l": list(fixed_top_l),
        "results_sha256": sha256_file(results_path),
        "fixed_top_l_sha256": sha256_file(fixed_path),
        "result_rows": len(rows),
        "fixed_top_l_rows": len(fixed_rows),
        "qrels_sha256": sha256_file(qrels_path),
        "ranking_store_sha256": sha256_file(store_path),
        "protocol_file_sha256": {
            str(path.relative_to(root)): sha256_file(path)
            for path in sorted((root / "configs").rglob("*.yaml"))
        },
    }
    write_json(output_directory / f"{output_id}-manifest.json", manifest)
    return results_path, fixed_path
