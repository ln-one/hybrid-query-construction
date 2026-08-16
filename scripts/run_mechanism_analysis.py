from __future__ import annotations

import argparse
import json
import sqlite3
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd
import yaml
import zstandard as zstd
from scipy.stats import spearmanr

from hybrid_query_construction.datasets import load_qrels
from hybrid_query_construction.io import read_jsonl, sha256_bytes, sha256_file, write_json
from hybrid_query_construction.mechanism import dense_geometry, sparse_reordering
from hybrid_query_construction.retrieval import DenseEncoder

DATASETS = (
    "scifact",
    "nfcorpus",
    "trec-covid",
    "fiqa",
    "arguana",
    "webis-touche2020",
    "scidocs",
)
METHODS = ("original", "dense_only", "sparse_only", "proposed")


class ReadOnlyRankingStore:
    def __init__(self, path: Path) -> None:
        self.connection = sqlite3.connect(f"file:{path}?mode=ro", uri=True)
        row = self.connection.execute(
            "SELECT value FROM metadata WHERE key='documents_json'"
        ).fetchone()
        if row is None:
            raise RuntimeError(f"missing document metadata in {path}")
        self.document_ids = tuple(json.loads(row[0]))
        self.ordinals = {
            document_id: index for index, document_id in enumerate(self.document_ids)
        }
        dataset_row = self.connection.execute(
            "SELECT value FROM metadata WHERE key='dataset'"
        ).fetchone()
        if dataset_row is None:
            raise RuntimeError(f"missing dataset metadata in {path}")
        self.dataset = str(dataset_row[0])

    def close(self) -> None:
        self.connection.close()

    def get(
        self,
        *,
        query_id: str,
        draw_id: int,
        track: str,
        channel: str,
        reference_count: int,
    ) -> np.ndarray[Any, np.dtype[np.uint32]]:
        row = self.connection.execute(
            """SELECT ranking, ranking_sha256 FROM rankings
            WHERE dataset=? AND query_id=? AND draw_id=? AND track=? AND channel=?
            AND reference_count=?""",
            (self.dataset, query_id, draw_id, track, channel, reference_count),
        ).fetchone()
        if row is None:
            raise KeyError((query_id, draw_id, track, channel, reference_count))
        raw = zstd.ZstdDecompressor().decompress(row[0])
        if sha256_bytes(raw) != row[1]:
            raise RuntimeError("ranking artifact hash mismatch")
        return np.frombuffer(raw, dtype="<u4").copy()


def _results(root: Path, dataset: str) -> dict[tuple[str, int, str], dict[str, Any]]:
    rows = read_jsonl(root / "artifacts" / "results" / "raw" / f"{dataset}.jsonl")
    return {
        (str(row["query_id"]), int(row["draw_id"]), str(row["method"])): row
        for row in rows
        if row["track"] == "controlled"
        and row["condition_id"] == "primary"
        and int(row["reference_count"]) == 5
        and int(row["rrf_constant"]) == 60
        and row["method"] in METHODS
    }


def _favorable_depth_reduction(original: float, current: float) -> float:
    return 0.0 if original == 0.0 else 100.0 * (1.0 - current / original)


def _outcome_fields(
    lookup: dict[tuple[str, int, str], dict[str, Any]], query_id: str, draw_id: int
) -> dict[str, float]:
    original = lookup[(query_id, draw_id, "original")]
    output: dict[str, float] = {}
    for method in ("dense_only", "sparse_only", "proposed"):
        current = lookup[(query_id, draw_id, method)]
        output[f"{method}_delta_ndcg"] = float(current["ndcg_at_10"]) - float(
            original["ndcg_at_10"]
        )
        output[f"{method}_delta_recall"] = float(current["recall_at_20"]) - float(
            original["recall_at_20"]
        )
        output[f"{method}_dense_depth_reduction_pct"] = _favorable_depth_reduction(
            float(original["dense_depth"]), float(current["dense_depth"])
        )
        output[f"{method}_sparse_depth_reduction_pct"] = _favorable_depth_reduction(
            float(original["sparse_depth"]), float(current["sparse_depth"])
        )
    return output


def _dataset_rows(
    root: Path,
    dataset: str,
    encoder: DenseEncoder,
    instruction: str,
    batch_size: int,
) -> list[dict[str, Any]]:
    generation_path = root / "artifacts" / "generations" / "bridge" / f"{dataset}.jsonl"
    records = [
        row
        for row in read_jsonl(generation_path)
        if row["status"] == "ok" and len(row["parsed_references"]) >= 5
    ]
    records.sort(key=lambda row: (str(row["query_id"]), int(row["draw_id"])))
    query_texts = {
        str(record["query_id"]): str(record["query_text"]) for record in records
    }
    query_ids = sorted(query_texts)
    original_vectors = encoder.encode_queries(
        [query_texts[query_id] for query_id in query_ids], instruction, batch_size=batch_size
    )
    original_by_query = dict(zip(query_ids, original_vectors, strict=True))

    pair_texts: list[str] = []
    pair_slices: list[tuple[int, int]] = []
    for record in records:
        start = len(pair_texts)
        query = str(record["query_text"])
        pair_texts.extend(
            f"{query} [SEP] {reference}"
            for reference in record["parsed_references"][:5]
        )
        pair_slices.append((start, len(pair_texts)))
    pair_vectors = encoder.encode_queries(pair_texts, instruction, batch_size=batch_size)

    qrels = load_qrels(root / "data" / "processed" / dataset / "qrels.tsv")
    outcomes = _results(root, dataset)
    store = ReadOnlyRankingStore(
        root / "artifacts" / "rankings" / dataset / "rankings.sqlite3"
    )
    ordinal_qrels = {
        query_id: {
            store.ordinals[document_id]: grade
            for document_id, grade in judgments.items()
            if document_id in store.ordinals
        }
        for query_id, judgments in qrels.items()
    }
    original_sparse: dict[str, np.ndarray[Any, np.dtype[np.uint32]]] = {}
    rows: list[dict[str, Any]] = []
    try:
        for record, (start, end) in zip(records, pair_slices, strict=True):
            query_id = str(record["query_id"])
            draw_id = int(record["draw_id"])
            geometry = dense_geometry(
                original_by_query[query_id],
                pair_vectors[start:end],
            )
            if query_id not in original_sparse:
                original_sparse[query_id] = store.get(
                    query_id=query_id,
                    draw_id=0,
                    track="base",
                    channel="sparse_original",
                    reference_count=0,
                )
            anchored = store.get(
                query_id=query_id,
                draw_id=draw_id,
                track="controlled",
                channel="sparse_anchor",
                reference_count=5,
            )
            reordering = sparse_reordering(
                original_sparse[query_id], anchored, ordinal_qrels[query_id]
            )
            rows.append(
                {
                    "dataset": dataset,
                    "query_id": query_id,
                    "draw_id": draw_id,
                    "dense_residual_norm": geometry.residual_norm,
                    "dense_angle_degrees": geometry.angle_degrees,
                    "sparse_support_equal": reordering.support_equal,
                    "sparse_support_retention": reordering.support_retention,
                    "sparse_missing_documents": reordering.missing_documents,
                    "sparse_top20_overlap": reordering.top20_overlap,
                    "sparse_top20_turnover": 1.0 - reordering.top20_overlap,
                    "sparse_top100_overlap": reordering.top100_overlap,
                    "sparse_relevant_rr_delta": (
                        reordering.relevant_reciprocal_rank_delta
                    ),
                    "sparse_relevant_mean_rank_gain": reordering.relevant_mean_rank_gain,
                    "sparse_ranked_relevant_documents": (
                        reordering.ranked_relevant_documents
                    ),
                    **_outcome_fields(outcomes, query_id, draw_id),
                }
            )
    finally:
        store.close()
    return rows


def _query_means(per_draw: pd.DataFrame) -> pd.DataFrame:
    numeric = [
        column
        for column in per_draw.columns
        if column not in {"dataset", "query_id", "draw_id", "sparse_support_equal"}
    ]
    means = per_draw.groupby(["dataset", "query_id"], as_index=False)[numeric].mean()
    support = per_draw.groupby(["dataset", "query_id"], as_index=False)[
        "sparse_support_equal"
    ].all()
    return means.merge(support, on=["dataset", "query_id"], validate="one_to_one")


def _summary(per_query: pd.DataFrame, per_draw: pd.DataFrame) -> pd.DataFrame:
    metrics = {
        "queries": ("query_id", "nunique"),
        "dense_angle_mean": ("dense_angle_degrees", "mean"),
        "dense_angle_median": ("dense_angle_degrees", "median"),
        "dense_angle_p95": ("dense_angle_degrees", lambda values: values.quantile(0.95)),
        "dense_angle_max": ("dense_angle_degrees", "max"),
        "dense_residual_norm_mean": ("dense_residual_norm", "mean"),
        "sparse_top20_turnover_mean": ("sparse_top20_turnover", "mean"),
        "sparse_top100_overlap_mean": ("sparse_top100_overlap", "mean"),
        "sparse_relevant_rr_delta_mean": ("sparse_relevant_rr_delta", "mean"),
        "dense_only_delta_ndcg": ("dense_only_delta_ndcg", "mean"),
        "dense_only_dense_depth_reduction_pct": (
            "dense_only_dense_depth_reduction_pct",
            "mean",
        ),
        "sparse_only_delta_ndcg": ("sparse_only_delta_ndcg", "mean"),
        "sparse_only_sparse_depth_reduction_pct": (
            "sparse_only_sparse_depth_reduction_pct",
            "mean",
        ),
    }
    detail = per_query.groupby("dataset", as_index=False).agg(**metrics)
    support = (
        per_draw.groupby("dataset", as_index=False)
        .agg(
            exact_support_query_draw_rate=("sparse_support_equal", "mean"),
            support_retention_mean=("sparse_support_retention", "mean"),
            missing_document_occurrences=("sparse_missing_documents", "sum"),
        )
    )
    detail = detail.merge(support, on="dataset", validate="one_to_one")
    macro = {"dataset": "macro_equal_dataset", "queries": int(detail["queries"].sum())}
    for column in detail.columns:
        if column not in {"dataset", "queries"}:
            macro[column] = float(
                detail[column].sum()
                if column == "missing_document_occurrences"
                else detail[column].mean()
            )
    return pd.concat([detail, pd.DataFrame([macro])], ignore_index=True)


def _correlations(per_query: pd.DataFrame) -> pd.DataFrame:
    pairs = (
        (
            "dense_angle_degrees",
            "dense_only_delta_ndcg",
            "dense_angle_vs_dense_only_delta_ndcg",
        ),
        (
            "dense_angle_degrees",
            "dense_only_dense_depth_reduction_pct",
            "dense_angle_vs_dense_depth_reduction",
        ),
        (
            "sparse_top20_turnover",
            "sparse_only_delta_ndcg",
            "sparse_turnover_vs_sparse_only_delta_ndcg",
        ),
        (
            "sparse_top20_turnover",
            "sparse_only_sparse_depth_reduction_pct",
            "sparse_turnover_vs_sparse_depth_reduction",
        ),
        (
            "sparse_relevant_rr_delta",
            "sparse_only_delta_ndcg",
            "relevant_rr_gain_vs_sparse_only_delta_ndcg",
        ),
    )
    rows: list[dict[str, Any]] = []
    for dataset, data in per_query.groupby("dataset", sort=True):
        for left, right, analysis in pairs:
            coefficient, pvalue = spearmanr(data[left], data[right], nan_policy="omit")
            rows.append(
                {
                    "dataset": dataset,
                    "analysis": analysis,
                    "queries": len(data),
                    "spearman_rho": float(coefficient),
                    "pvalue_descriptive": float(pvalue),
                }
            )
    frame = pd.DataFrame(rows)
    macro = (
        frame.groupby("analysis", as_index=False)
        .agg(
            queries=("queries", "sum"),
            spearman_rho=("spearman_rho", "mean"),
        )
        .assign(dataset="macro_equal_dataset", pvalue_descriptive=np.nan)
    )
    return pd.concat([frame, macro], ignore_index=True)


def _binned_effects(per_query: pd.DataFrame) -> pd.DataFrame:
    specifications = (
        (
            "dense",
            "dense_angle_degrees",
            "dense_only_delta_ndcg",
            "dense_only_dense_depth_reduction_pct",
        ),
        (
            "sparse",
            "sparse_top20_turnover",
            "sparse_only_delta_ndcg",
            "sparse_only_sparse_depth_reduction_pct",
        ),
    )
    rows: list[dict[str, Any]] = []
    for dataset, data in per_query.groupby("dataset", sort=True):
        for mechanism, driver, quality, depth in specifications:
            ranked = data[driver].rank(method="average", pct=True)
            bins = np.ceil(ranked * 4.0).clip(1, 4).astype(int)
            working = data.assign(mechanism_bin=bins)
            for bin_id, group in working.groupby("mechanism_bin", sort=True):
                rows.append(
                    {
                        "dataset": dataset,
                        "mechanism": mechanism,
                        "bin": int(bin_id),
                        "queries": len(group),
                        "driver_mean": float(group[driver].mean()),
                        "delta_ndcg": float(group[quality].mean()),
                        "depth_reduction_pct": float(group[depth].mean()),
                    }
                )
    detail = pd.DataFrame(rows)
    macro = (
        detail.groupby(["mechanism", "bin"], as_index=False)
        .agg(
            queries=("queries", "sum"),
            driver_mean=("driver_mean", "mean"),
            delta_ndcg=("delta_ndcg", "mean"),
            depth_reduction_pct=("depth_reduction_pct", "mean"),
        )
        .assign(dataset="macro_equal_dataset")
    )
    return pd.concat([detail, macro], ignore_index=True)


def _cache_signature(root: Path, dataset: str, config_path: Path) -> dict[str, str]:
    inputs = {
        "config": config_path,
        "generation": root / "artifacts" / "generations" / "bridge" / f"{dataset}.jsonl",
        "qrels": root / "data" / "processed" / dataset / "qrels.tsv",
        "ranking_manifest": (
            root / "artifacts" / "rankings" / dataset / "rankings-manifest.json"
        ),
        "results": root / "artifacts" / "results" / "raw" / f"{dataset}.jsonl",
        "analysis_script": Path(__file__).resolve(),
        "mechanism_module": (
            root / "src" / "hybrid_query_construction" / "mechanism.py"
        ),
    }
    return {name: sha256_file(path) for name, path in inputs.items()}


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, default=Path.cwd())
    parser.add_argument("--device", default="mps")
    parser.add_argument("--batch-size", type=int, default=256)
    parser.add_argument("--datasets", nargs="*", default=list(DATASETS))
    parser.add_argument("--force", action="store_true")
    args = parser.parse_args()
    root = args.root.resolve()
    config_path = root / "configs" / "retrievers" / "formal-v1.yaml"
    config = yaml.safe_load(config_path.read_text(encoding="utf-8"))
    dense_config = config["dense"]
    encoder = DenseEncoder(
        dense_config["model_id"], dense_config["revision"], device=args.device
    )

    rows: list[dict[str, Any]] = []
    cache_directory = root / "artifacts" / "traces" / "mechanism"
    cache_directory.mkdir(parents=True, exist_ok=True)
    for dataset in args.datasets:
        cache_path = cache_directory / f"{dataset}.csv"
        cache_manifest_path = cache_directory / f"{dataset}-manifest.json"
        signature = _cache_signature(root, dataset, config_path)
        cached = False
        if cache_path.exists() and cache_manifest_path.exists() and not args.force:
            cache_manifest = json.loads(cache_manifest_path.read_text(encoding="utf-8"))
            cached = cache_manifest.get("input_sha256") == signature
        if cached:
            print(f"mechanism analysis: {dataset} (cached)", flush=True)
            dataset_frame = pd.read_csv(cache_path, dtype={"query_id": str})
        else:
            print(f"mechanism analysis: {dataset}", flush=True)
            dataset_frame = pd.DataFrame(
                _dataset_rows(
                    root,
                    dataset,
                    encoder,
                    dense_config["query_instruction"],
                    args.batch_size,
                )
            )
            dataset_frame.to_csv(cache_path, index=False)
            write_json(
                cache_manifest_path,
                {
                    "schema_version": 1,
                    "dataset": dataset,
                    "input_sha256": signature,
                    "rows": len(dataset_frame),
                    "output_sha256": sha256_file(cache_path),
                },
            )
        rows.extend(dataset_frame.to_dict(orient="records"))
    per_draw = pd.DataFrame(rows).sort_values(["dataset", "query_id", "draw_id"])
    per_query = _query_means(per_draw).sort_values(["dataset", "query_id"])
    summary = _summary(per_query, per_draw)
    correlations = _correlations(per_query)
    binned = _binned_effects(per_query)

    report = root / "report"
    figure_data = root / "figures" / "data"
    report.mkdir(parents=True, exist_ok=True)
    figure_data.mkdir(parents=True, exist_ok=True)
    outputs = {
        "per_draw": report / "mechanism-per-draw.csv",
        "per_query": report / "mechanism-per-query.csv",
        "summary": report / "mechanism-summary.csv",
        "correlations": report / "mechanism-correlations.csv",
        "binned_effects": figure_data / "mechanism-binned-effects.csv",
        "distribution": figure_data / "mechanism-distributions.csv",
    }
    per_draw.to_csv(outputs["per_draw"], index=False)
    per_query.to_csv(outputs["per_query"], index=False)
    summary.to_csv(outputs["summary"], index=False)
    correlations.to_csv(outputs["correlations"], index=False)
    binned.to_csv(outputs["binned_effects"], index=False)
    per_query[
        [
            "dataset",
            "query_id",
            "dense_angle_degrees",
            "dense_residual_norm",
            "sparse_top20_turnover",
            "sparse_top100_overlap",
        ]
    ].to_csv(outputs["distribution"], index=False)
    write_json(
        report / "mechanism-manifest.json",
        {
            "schema_version": 1,
            "analysis": "desa-mechanism-v1",
            "datasets": list(args.datasets),
            "draw_aggregation": "arithmetic mean within query",
            "dataset_aggregation": "equal-dataset macro mean",
            "dense_encoder": dense_config,
            "generation_source": "artifacts/generations/bridge/<dataset>.jsonl",
            "ranking_source": "artifacts/rankings/<dataset>/rankings.sqlite3",
            "result_source": "artifacts/results/raw/<dataset>.jsonl",
            "config_sha256": sha256_file(config_path),
            "outputs": {
                name: {"path": str(path.relative_to(root)), "sha256": sha256_file(path)}
                for name, path in outputs.items()
            },
        },
    )


if __name__ == "__main__":
    main()
