from __future__ import annotations

import argparse
import os
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path

import pandas as pd

from hybrid_query_construction.datasets import load_qrels
from hybrid_query_construction.evidence import (
    fixed_cutoff_diagnostics,
    paired_quality_tests,
    qudar_simple_rrf,
)
from hybrid_query_construction.fusion import complete_wrrf
from hybrid_query_construction.io import (
    atomic_write_text,
    canonical_json,
    read_jsonl,
    sha256_file,
    write_json,
)
from hybrid_query_construction.metrics import ndcg_at_k, recall_at_k
from hybrid_query_construction.storage import RankingStore, ranking_store_digest

DATASETS = (
    "scifact",
    "nfcorpus",
    "trec-covid",
    "fiqa",
    "arguana",
    "webis-touche2020",
    "scidocs",
)

def _load_raw(directory: Path, *, fixed: bool) -> pd.DataFrame:
    pattern = "*-fixed-top-l.jsonl" if fixed else "*.jsonl"
    rows: list[dict[str, object]] = []
    for path in sorted(directory.glob(pattern)):
        if not fixed and "fixed-top-l" in path.name:
            continue
        rows.extend(read_jsonl(path))
    return pd.DataFrame(rows)


def _artifact(
    store: RankingStore,
    spec: str,
    *,
    query_id: str,
    draw_id: int,
    reference_count: int = 5,
):
    track, channel = spec.split(":", maxsplit=1)
    return store.get(
        query_id=query_id,
        draw_id=0 if track == "base" else draw_id,
        track=track,
        channel=channel,
        reference_count=0 if track == "base" else reference_count,
    )


def _write_jsonl(path: Path, rows: list[dict[str, object]]) -> None:
    atomic_write_text(path, "".join(canonical_json(row) + "\n" for row in rows))


def _aggregate(frame: pd.DataFrame, metrics: list[str]) -> pd.DataFrame:
    dataset = frame.groupby(["dataset", "method"], as_index=False)[metrics].mean()
    macro = dataset.groupby("method", as_index=False)[metrics].mean()
    macro.insert(0, "dataset", "macro_equal_dataset")
    return pd.concat([dataset, macro], ignore_index=True)


def _evaluate_dataset(
    root_string: str, dataset: str
) -> tuple[list[dict[str, object]], list[dict[str, object]], str]:
    root = Path(root_string)
    store_path = root / "artifacts" / "rankings" / dataset / "rankings.sqlite3"
    document_ids = RankingStore.load_document_ids(store_path)
    qrels = load_qrels(root / "data" / "processed" / dataset / "qrels.tsv")
    operator_rows: list[dict[str, object]] = []
    qudar_rows: list[dict[str, object]] = []
    with RankingStore(store_path, dataset, document_ids) as store:
        draws = sorted(
            {
                (query_id, draw_id)
                for query_id, draw_id, track, channel, count in store.keys()
                if track == "controlled"
                and channel == "dense_residual"
                and count == 5
                and query_id in qrels
            }
        )
        for query_id, draw_id in draws:
            os = _artifact(
                store,
                "base:sparse_original",
                query_id=query_id,
                draw_id=draw_id,
            )
            od = _artifact(
                store,
                "base:dense_original",
                query_id=query_id,
                draw_id=draw_id,
            )
            es = _artifact(
                store,
                "controlled:sparse_rewrite",
                query_id=query_id,
                draw_id=draw_id,
            )
            ed = _artifact(
                store,
                "controlled:dense_contextual",
                query_id=query_id,
                draw_id=draw_id,
            )
            for method, dense, sparse in (
                ("dense_contextual", ed, os),
                ("sparse_rewrite", od, es),
            ):
                fused = complete_wrrf(
                    (dense.ranking, sparse.ranking), top_k=20, constant=60
                )
                operator_rows.append(
                    {
                        "dataset": dataset,
                        "query_id": query_id,
                        "draw_id": draw_id,
                        "method": method,
                        "ndcg_at_10": ndcg_at_k(fused, qrels[query_id], 10),
                        "recall_at_20": recall_at_k(fused, qrels[query_id], 20),
                        "dense_ranking_sha256": dense.ranking_sha256,
                        "sparse_ranking_sha256": sparse.ranking_sha256,
                    }
                )

            fused = qudar_simple_rrf(
                (os.ranking, od.ranking, es.ranking, ed.ranking),
                retrieval_depth=1000,
                top_k=20,
                constant=60,
            )
            qudar_rows.append(
                {
                    "dataset": dataset,
                    "query_id": query_id,
                    "draw_id": draw_id,
                    "method": "qudar_simple_rrf_matched",
                    "ndcg_at_10": ndcg_at_k(fused, qrels[query_id], 10),
                    "recall_at_20": recall_at_k(fused, qrels[query_id], 20),
                    "retrieval_depth_per_signal": 1000,
                    "rrf_constant": 60,
                    "ranking_sha256": {
                        "os": os.ranking_sha256,
                        "od": od.ranking_sha256,
                        "es": es.ranking_sha256,
                        "ed": ed.ranking_sha256,
                    },
                }
            )
    return operator_rows, qudar_rows, ranking_store_digest(store_path)


def run(root: Path) -> None:
    raw_directory = root / "artifacts" / "results" / "raw"
    report_directory = root / "report"
    derived_directory = root / "artifacts" / "results" / "derived"
    report_directory.mkdir(parents=True, exist_ok=True)
    derived_directory.mkdir(parents=True, exist_ok=True)

    complete = _load_raw(raw_directory, fixed=False)
    fixed = _load_raw(raw_directory, fixed=True)
    selection = (
        complete["dataset"].isin(DATASETS)
        & (complete["track"] == "controlled")
        & (complete["condition_id"] == "primary")
        & (complete["reference_count"] == 5)
        & (complete["rrf_constant"] == 60)
    )
    complete_primary = complete[selection]
    fixed_selection = (
        fixed["dataset"].isin(DATASETS)
        & (fixed["track"] == "controlled")
        & (fixed["condition_id"] == "primary")
        & (fixed["reference_count"] == 5)
        & (fixed["rrf_constant"] == 60)
    )
    diagnostics, conclusions = fixed_cutoff_diagnostics(
        complete_primary,
        fixed[fixed_selection],
        methods=("original", "bridge_shared", "proposed"),
    )
    diagnostics.to_csv(report_directory / "fixed-top-l-query-diagnostics.csv", index=False)
    conclusions.to_csv(
        report_directory / "fixed-top-l-conclusion-changes.csv", index=False
    )

    operator_rows: list[dict[str, object]] = []
    qudar_rows: list[dict[str, object]] = []
    ranking_hashes: dict[str, str] = {}
    workers = min(len(DATASETS), os.cpu_count() or 1)
    with ProcessPoolExecutor(max_workers=workers) as executor:
        futures = {
            dataset: executor.submit(_evaluate_dataset, str(root), dataset)
            for dataset in DATASETS
        }
        for dataset in DATASETS:
            dataset_operator, dataset_qudar, digest = futures[dataset].result()
            operator_rows.extend(dataset_operator)
            qudar_rows.extend(dataset_qudar)
            ranking_hashes[dataset] = digest

    operator_path = derived_directory / "operator-controls.jsonl"
    qudar_path = derived_directory / "qudar-simple-rrf-matched.jsonl"
    _write_jsonl(operator_path, operator_rows)
    _write_jsonl(qudar_path, qudar_rows)

    existing_operator = complete_primary[
        complete_primary["method"].isin(("original", "dense_only", "sparse_only"))
    ][
        ["dataset", "query_id", "draw_id", "method", "ndcg_at_10", "recall_at_20"]
    ].copy()
    existing_operator["method"] = existing_operator["method"].replace(
        {"dense_only": "dense_residual", "sparse_only": "sparse_product"}
    )
    operator_frame = pd.concat(
        [existing_operator, pd.DataFrame(operator_rows)], ignore_index=True
    )
    operator_summary = _aggregate(
        operator_frame,
        ["ndcg_at_10", "recall_at_20"],
    )
    operator_summary.to_csv(report_directory / "operator-control-results.csv", index=False)
    pd.concat(
        [
            paired_quality_tests(
                operator_frame,
                proposed="dense_residual",
                comparator="dense_contextual",
            ),
            paired_quality_tests(
                operator_frame,
                proposed="sparse_product",
                comparator="sparse_rewrite",
            ),
        ],
        ignore_index=True,
    ).to_csv(report_directory / "operator-control-paired-tests.csv", index=False)

    desa = complete_primary[complete_primary["method"] == "proposed"][[
        "dataset",
        "query_id",
        "draw_id",
        "ndcg_at_10",
        "recall_at_20",
    ]].copy()
    desa["method"] = "desa"
    qudar_frame = pd.DataFrame(qudar_rows)
    comparison = pd.concat(
        [
            desa,
            qudar_frame[
                ["dataset", "query_id", "draw_id", "method", "ndcg_at_10", "recall_at_20"]
            ],
        ],
        ignore_index=True,
    )
    _aggregate(comparison, ["ndcg_at_10", "recall_at_20"]).to_csv(
        report_directory / "qudar-baseline-results.csv", index=False
    )
    paired_quality_tests(
        comparison,
        proposed="desa",
        comparator="qudar_simple_rrf_matched",
    ).to_csv(report_directory / "qudar-paired-tests.csv", index=False)

    write_json(
        report_directory / "evidence-strengthening-manifest.json",
        {
            "schema_version": 1,
            "datasets": list(DATASETS),
            "fixed_diagnostics_sha256": sha256_file(
                report_directory / "fixed-top-l-query-diagnostics.csv"
            ),
            "fixed_conclusions_sha256": sha256_file(
                report_directory / "fixed-top-l-conclusion-changes.csv"
            ),
            "operator_controls_sha256": sha256_file(operator_path),
            "qudar_simple_rrf_matched_sha256": sha256_file(qudar_path),
            "ranking_store_sha256": ranking_hashes,
            "qudar_specification": {
                "variant": "QuDAR-simple RRF",
                "official_code_commit": "0702721e82799d0489850d3f94ac787da43436ad",
                "official_repository": "https://github.com/kaist-dmlab/QuDAR",
                "retrieval_depth_per_signal": 1000,
                "rrf_constant": 60,
                "signals": ["OS", "OD", "ES", "ED"],
                "expanded_signals": "DESA matched generated evidence",
            },
        },
    )


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, default=Path.cwd())
    args = parser.parse_args()
    run(args.root.resolve())


if __name__ == "__main__":
    main()
