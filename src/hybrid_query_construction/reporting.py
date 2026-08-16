from __future__ import annotations

from pathlib import Path
from typing import Any

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from .io import atomic_write_text, read_jsonl
from .statistics import (
    holm_adjust,
    stratified_macro_bootstrap,
    stratified_paired_statistic_bootstrap,
    stratified_sign_flip_pvalue,
)

PRIMARY_METRICS = ("ndcg_at_10", "recall_at_20", "dense_depth", "sparse_depth")
COMPARATORS = ("original", "bridge_shared")
EVALUATION_DATASETS = (
    "scifact",
    "nfcorpus",
    "trec-covid",
    "fiqa",
    "arguana",
    "webis-touche2020",
    "scidocs",
)
FIDELITY_DATASETS = ("fiqa", "arguana", "webis-touche2020", "scidocs")


def load_result_rows(input_directory: Path) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for path in sorted(input_directory.rglob("*.jsonl")):
        if "fixed-top-l" not in path.name:
            rows.extend(read_jsonl(path))
    return rows


def load_fixed_top_l_rows(input_directory: Path) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for path in sorted(input_directory.rglob("*-fixed-top-l.jsonl")):
        rows.extend(read_jsonl(path))
    return rows


def load_generation_rows(root: Path) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for path in sorted((root / "artifacts" / "generations").rglob("*.jsonl")):
        if "compat" in path.parts:
            continue
        for record in read_jsonl(path):
            attempts = record.get("attempts", [])
            rows.append(
                {
                    "dataset": record["dataset"],
                    "model_id": record["model_id"],
                    "prompt_path": record["prompt_path"],
                    "query_id": record["query_id"],
                    "draw_id": record["draw_id"],
                    "prompt_tokens": sum(int(item["prompt_tokens"]) for item in attempts),
                    "completion_tokens": sum(
                        int(item["completion_tokens"]) for item in attempts
                    ),
                    "attempts": len(attempts),
                    "failed": record["status"] != "ok",
                }
            )
    return rows


def _query_means(frame: pd.DataFrame) -> pd.DataFrame:
    return (
        frame.groupby(
            [
                "dataset",
                "query_id",
                "track",
                "condition_id",
                "method",
                "reference_count",
                "rrf_constant",
            ],
            as_index=False,
        )
        .agg(
            ndcg_at_10=("ndcg_at_10", "mean"),
            recall_at_20=("recall_at_20", "mean"),
            dense_depth=("dense_depth", "mean"),
            sparse_depth=("sparse_depth", "mean"),
            sparse_support=("sparse_support", "mean"),
            sparse_exhausted=("sparse_exhausted", "mean"),
            fallback=("fallback", "mean"),
        )
        .sort_values(
            [
                "dataset",
                "track",
                "condition_id",
                "reference_count",
                "rrf_constant",
                "method",
                "query_id",
            ]
        )
    )


def _summary(query_means: pd.DataFrame) -> pd.DataFrame:
    return (
        query_means.groupby(
            [
                "dataset",
                "track",
                "condition_id",
                "method",
                "reference_count",
                "rrf_constant",
            ],
            as_index=False,
        )
        .agg(
            queries=("query_id", "nunique"),
            ndcg_at_10=("ndcg_at_10", "mean"),
            recall_at_20=("recall_at_20", "mean"),
            dense_depth=("dense_depth", "mean"),
            sparse_depth=("sparse_depth", "mean"),
            sparse_support=("sparse_support", "mean"),
            sparse_exhaustion_rate=("sparse_exhausted", "mean"),
            fallback_rate=("fallback", "mean"),
        )
        .sort_values(
            [
                "dataset",
                "track",
                "condition_id",
                "reference_count",
                "rrf_constant",
                "method",
            ]
        )
    )


def _access_changes(query_means: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    controlled = query_means[
        (query_means["track"] == "controlled")
        & (query_means["condition_id"] == "primary")
        & (query_means["reference_count"] == 5)
        & (query_means["rrf_constant"] == 60)
    ]
    paired_by_method: dict[str, dict[str, np.ndarray]] = {}
    rows: list[dict[str, object]] = []
    for dataset, data in controlled.groupby("dataset"):
        original = data[data["method"] == "original"].set_index("query_id")
        for method, method_data in data.groupby("method"):
            current = method_data.set_index("query_id")
            common = original.index.intersection(current.index)
            if common.empty:
                continue
            paired = np.column_stack(
                [
                    original.loc[common, "dense_depth"].to_numpy(float),
                    original.loc[common, "sparse_depth"].to_numpy(float),
                    current.loc[common, "dense_depth"].to_numpy(float),
                    current.loc[common, "sparse_depth"].to_numpy(float),
                ]
            )
            paired_by_method.setdefault(str(method), {})[str(dataset)] = paired
            dense_original, sparse_original, dense_current, sparse_current = paired.T
            rows.append(
                {
                    "dataset": dataset,
                    "method": method,
                    "dense_total_reduction_pct": 100.0
                    * (1.0 - dense_current.sum() / dense_original.sum()),
                    "sparse_total_reduction_pct": 100.0
                    * (1.0 - sparse_current.sum() / sparse_original.sum()),
                    "dual_depth_improvement_rate": float(
                        np.mean(
                            (dense_current < dense_original)
                            & (sparse_current < sparse_original)
                        )
                    ),
                }
            )
    statistics = {
        "dense_total_reduction_pct": lambda array: (
            100.0 * (1.0 - array[:, 2].sum() / array[:, 0].sum())
        ),
        "sparse_total_reduction_pct": lambda array: (
            100.0 * (1.0 - array[:, 3].sum() / array[:, 1].sum())
        ),
        "dual_depth_improvement_rate": lambda array: float(
            np.mean((array[:, 2] < array[:, 0]) & (array[:, 3] < array[:, 1]))
        ),
    }
    interval_rows: list[dict[str, object]] = []
    for method, by_dataset in paired_by_method.items():
        for metric, statistic in statistics.items():
            estimate, lower, upper = stratified_paired_statistic_bootstrap(
                by_dataset, statistic
            )
            interval_rows.append(
                {
                    "dataset": "macro_equal_dataset",
                    "method": method,
                    "metric": metric,
                    "estimate": estimate,
                    "ci95_lower": lower,
                    "ci95_upper": upper,
                }
            )
    detail = pd.DataFrame(rows).sort_values(["dataset", "method"])
    intervals = pd.DataFrame(interval_rows).sort_values(["method", "metric"])
    return detail, intervals


def _paired_tests(query_means: pd.DataFrame) -> pd.DataFrame:
    controlled = query_means[
        (query_means["track"] == "controlled")
        & (query_means["condition_id"] == "primary")
        & (query_means["reference_count"] == 5)
        & (query_means["rrf_constant"] == 60)
    ]
    proposed = controlled[controlled["method"] == "proposed"]
    rows: list[dict[str, object]] = []
    for comparator in COMPARATORS:
        baseline = controlled[controlled["method"] == comparator]
        paired = proposed.merge(
            baseline,
            on=["dataset", "query_id"],
            suffixes=("_proposed", "_comparator"),
            validate="one_to_one",
        )
        comparator_rows: list[dict[str, object]] = []
        comparator_pvalues: dict[str, float] = {}
        for metric in PRIMARY_METRICS:
            favorable = (
                paired[f"{metric}_proposed"] - paired[f"{metric}_comparator"]
                if metric in {"ndcg_at_10", "recall_at_20"}
                else paired[f"{metric}_comparator"] - paired[f"{metric}_proposed"]
            )
            differences = {
                dataset: group.to_list()
                for dataset, group in favorable.groupby(paired["dataset"])
            }
            estimate, lower, upper = stratified_macro_bootstrap(differences)
            pvalue = stratified_sign_flip_pvalue(differences)
            comparator_pvalues[metric] = pvalue
            comparator_rows.append(
                {
                    "comparison": f"proposed_vs_{comparator}",
                    "metric": metric,
                    "favorable_difference": estimate,
                    "ci95_lower": lower,
                    "ci95_upper": upper,
                    "p_raw": pvalue,
                }
            )
        adjusted = holm_adjust(comparator_pvalues)
        for row in comparator_rows:
            row["p_holm"] = adjusted[str(row["metric"])]
        rows.extend(comparator_rows)
    return pd.DataFrame(rows)


def _method_macro_intervals(query_means: pd.DataFrame) -> pd.DataFrame:
    controlled = query_means[
        (query_means["track"] == "controlled")
        & (query_means["condition_id"] == "primary")
        & (query_means["reference_count"] == 5)
        & (query_means["rrf_constant"] == 60)
    ]
    rows: list[dict[str, object]] = []
    for method, method_data in controlled.groupby("method", sort=True):
        for metric in PRIMARY_METRICS:
            values = {
                str(dataset): group[metric].to_list()
                for dataset, group in method_data.groupby("dataset")
            }
            estimate, lower, upper = stratified_macro_bootstrap(values)
            rows.append(
                {
                    "method": method,
                    "metric": metric,
                    "estimate": estimate,
                    "ci95_lower": lower,
                    "ci95_upper": upper,
                }
            )
    return pd.DataFrame(rows)


def _classify_confirmatory_outcomes(tests: pd.DataFrame) -> pd.DataFrame:
    rows: list[dict[str, object]] = []
    for comparison, data in tests.groupby("comparison", sort=True):
        if (data["ci95_lower"] > 0.0).all():
            label = "强阳性"
        elif (data["ci95_upper"] < 0.0).all():
            label = "负面"
        else:
            label = "混合"
        rows.append(
            {
                "comparison": comparison,
                "classification": label,
                "rule": "四项有利差值的95%区间同向，否则为混合",
            }
        )
    return pd.DataFrame(rows)


def _plot_quality_access(summary: pd.DataFrame, output: Path) -> None:
    controlled = summary[
        (summary["track"] == "controlled")
        & (summary["condition_id"] == "primary")
        & (summary["reference_count"] == 5)
        & (summary["rrf_constant"] == 60)
    ]
    macro = controlled.groupby("method", as_index=False)[
        ["ndcg_at_10", "dense_depth", "sparse_depth"]
    ].mean()
    fig, axes = plt.subplots(1, 2, figsize=(10.2, 4.4), sharey=True)
    for axis, depth, label in (
        (axes[0], "dense_depth", "Mean Dense stopping depth"),
        (axes[1], "sparse_depth", "Mean Sparse stopping depth"),
    ):
        axis.scatter(macro[depth], macro["ndcg_at_10"], color="#0072B2", s=45)
        for _, row in macro.iterrows():
            axis.annotate(
                row["method"],
                (row[depth], row["ndcg_at_10"]),
                xytext=(4, 4),
                textcoords="offset points",
                fontsize=8,
            )
        axis.set_xlabel(label)
        axis.grid(alpha=0.2)
    axes[0].set_ylabel("Dataset-macro nDCG@10")
    fig.tight_layout()
    fig.savefig(output, dpi=220)
    plt.close(fig)


def _plot_fixed_top_l(summary: pd.DataFrame, output: Path) -> None:
    selected = summary[
        summary["dataset"].isin(EVALUATION_DATASETS)
        & (summary["condition_id"] == "primary")
        & summary["method"].isin(("original", "bridge_shared", "proposed"))
        & (summary["reference_count"] == 5)
        & (summary["rrf_constant"] == 60)
    ]
    if selected.empty:
        return
    macro = selected.groupby(["method", "top_l"], as_index=False)[
        ["ndcg_at_10", "complete_top20_exact_rate"]
    ].mean()
    fig, axes = plt.subplots(1, 2, figsize=(10.2, 4.2))
    for method, data in macro.groupby("method"):
        axes[0].plot(data["top_l"], data["ndcg_at_10"], marker="o", label=method)
        axes[1].plot(data["top_l"], data["complete_top20_exact_rate"], marker="o", label=method)
    for axis in axes:
        axis.set_xscale("log")
        axis.set_xlabel("Fixed Top-L")
        axis.grid(alpha=0.2)
    axes[0].set_ylabel("Dataset-macro nDCG@10")
    axes[1].set_ylabel("Complete Top-20 exact rate")
    axes[1].legend(fontsize=8)
    fig.tight_layout()
    fig.savefig(output, dpi=220)
    plt.close(fig)


def _plot_scale_trends(summary: pd.DataFrame, output: Path) -> None:
    selected = summary[
        (summary["track"] == "scale")
        & (summary["condition_id"] == "primary")
        & summary["method"].isin(("original", "proposed"))
        & (summary["reference_count"] == 5)
        & (summary["rrf_constant"] == 60)
    ].copy()
    if selected.empty:
        return
    selected["documents"] = selected["dataset"].str.rsplit("-", n=1).str[-1].astype(int)
    fig, axes = plt.subplots(1, 2, figsize=(10.2, 4.2))
    for method, data in selected.sort_values("documents").groupby("method"):
        axes[0].plot(data["documents"], data["dense_depth"], marker="o", label=method)
        axes[1].plot(data["documents"], data["sparse_depth"], marker="o", label=method)
    for axis in axes:
        axis.set_xscale("log")
        axis.set_xlabel("Corpus documents")
        axis.grid(alpha=0.2)
    axes[0].set_ylabel("Mean Dense stopping depth")
    axes[1].set_ylabel("Mean Sparse stopping depth")
    axes[1].legend(fontsize=8)
    fig.tight_layout()
    fig.savefig(output, dpi=220)
    plt.close(fig)


def _markdown_or_empty(frame: pd.DataFrame, *, floatfmt: str = ".4f") -> str:
    if frame.empty:
        return "该实验轨道无记录。"
    return frame.to_markdown(index=False, floatfmt=floatfmt)


def _original_proposed_pairs(
    frame: pd.DataFrame,
    *,
    group_columns: tuple[str, ...],
) -> pd.DataFrame:
    """Build compact, explicit Original--Proposed comparisons for the report."""
    rows: list[dict[str, object]] = []
    for group_key, data in frame.groupby(list(group_columns), sort=True):
        key_values = group_key if isinstance(group_key, tuple) else (group_key,)
        original = data[data["method"] == "original"]
        proposed = data[data["method"] == "proposed"]
        if len(original) != 1 or len(proposed) != 1:
            continue
        left = original.iloc[0]
        right = proposed.iloc[0]
        row: dict[str, object] = dict(zip(group_columns, key_values, strict=True))
        row.update(
            {
                "original_ndcg": left["ndcg_at_10"],
                "proposed_ndcg": right["ndcg_at_10"],
                "delta_ndcg": right["ndcg_at_10"] - left["ndcg_at_10"],
                "original_recall": left["recall_at_20"],
                "proposed_recall": right["recall_at_20"],
                "delta_recall": right["recall_at_20"] - left["recall_at_20"],
                "dense_reduction_pct": 100.0
                * (1.0 - right["dense_depth"] / left["dense_depth"]),
                "sparse_reduction_pct": 100.0
                * (1.0 - right["sparse_depth"] / left["sparse_depth"]),
                "proposed_fallback_rate": right["fallback_rate"],
            }
        )
        rows.append(row)
    return pd.DataFrame(rows)


def build_report(
    input_directory: Path, output_directory: Path, root: Path | None = None
) -> Path:
    rows = load_result_rows(input_directory)
    if not rows:
        raise RuntimeError("no real per-query result records found")
    output_directory.mkdir(parents=True, exist_ok=True)
    frame = pd.DataFrame(rows)
    if "condition_id" not in frame:
        frame["condition_id"] = "primary"
    query_means = _query_means(frame)
    summary = _summary(query_means)
    evaluation_query_means = query_means[
        query_means["dataset"].isin(EVALUATION_DATASETS)
    ]
    access, access_intervals = _access_changes(evaluation_query_means)
    tests = _paired_tests(evaluation_query_means)
    method_intervals = _method_macro_intervals(evaluation_query_means)
    classifications = _classify_confirmatory_outcomes(tests)

    query_means.to_csv(output_directory / "per-query-draw-mean.csv", index=False)
    summary.to_csv(output_directory / "all-results.csv", index=False)
    evaluation_main = summary[
        summary["dataset"].isin(EVALUATION_DATASETS)
        & (summary["track"] == "controlled")
        & (summary["condition_id"] == "primary")
        & (summary["reference_count"] == 5)
        & (summary["rrf_constant"] == 60)
    ]
    evaluation_main.to_csv(output_directory / "main-results.csv", index=False)
    summary[
        summary["dataset"].isin(FIDELITY_DATASETS) & (summary["track"] == "fidelity")
    ].to_csv(output_directory / "fidelity-results.csv", index=False)
    summary[summary["track"] == "ablation"].to_csv(
        output_directory / "ablation-results.csv", index=False
    )
    summary[
        summary["track"].isin(("controlled", "ablation")) & (summary["rrf_constant"] == 60)
    ].to_csv(output_directory / "reference-count-results.csv", index=False)
    summary[
        summary["track"].isin(("controlled", "ablation")) & (summary["reference_count"] == 5)
    ].to_csv(output_directory / "rrf-constant-results.csv", index=False)
    summary[summary["track"] == "robustness"].to_csv(
        output_directory / "robustness-results.csv", index=False
    )
    summary[summary["track"] == "scale"].to_csv(
        output_directory / "scale-results.csv", index=False
    )
    access.to_csv(output_directory / "access-changes-vs-original.csv", index=False)
    access_intervals.to_csv(output_directory / "access-macro-bootstrap.csv", index=False)
    tests.to_csv(output_directory / "primary-paired-tests.csv", index=False)
    method_intervals.to_csv(output_directory / "main-macro-bootstrap.csv", index=False)
    classifications.to_csv(output_directory / "outcome-classification.csv", index=False)
    _plot_quality_access(evaluation_main, output_directory / "quality-access.png")

    fixed_summary = pd.DataFrame()
    fixed_rows = load_fixed_top_l_rows(input_directory)
    if fixed_rows:
        fixed_frame = pd.DataFrame(fixed_rows)
        fixed_summary = (
            fixed_frame.groupby(
                [
                    "dataset",
                    "track",
                    "condition_id",
                    "method",
                    "reference_count",
                    "rrf_constant",
                    "top_l",
                ],
                as_index=False,
            )
            .agg(
                ndcg_at_10=("ndcg_at_10", "mean"),
                recall_at_20=("recall_at_20", "mean"),
                complete_top20_exact_rate=("complete_top20_exact", "mean"),
            )
            .sort_values(
                [
                    "dataset",
                    "track",
                    "condition_id",
                    "method",
                    "reference_count",
                    "rrf_constant",
                    "top_l",
                ]
            )
        )
        fixed_summary.to_csv(output_directory / "fixed-top-l-results.csv", index=False)
        _plot_fixed_top_l(fixed_summary, output_directory / "fixed-top-l.png")

    _plot_scale_trends(summary, output_directory / "scale-trends.png")

    generation_summary = pd.DataFrame()
    if root is not None:
        generation_rows = load_generation_rows(root)
        if generation_rows:
            generation_summary = (
                pd.DataFrame(generation_rows)
                .groupby(["dataset", "model_id", "prompt_path"], as_index=False)
                .agg(
                    records=("query_id", "size"),
                    mean_prompt_tokens=("prompt_tokens", "mean"),
                    mean_completion_tokens=("completion_tokens", "mean"),
                    mean_attempts=("attempts", "mean"),
                    failure_rate=("failed", "mean"),
                )
                .sort_values(["dataset", "model_id", "prompt_path"])
            )
            generation_summary.to_csv(output_directory / "generation-costs.csv", index=False)

    controlled = evaluation_main
    macro = (
        controlled.groupby("method", as_index=False)[list(PRIMARY_METRICS)]
        .mean()
        .sort_values("method")
    )
    main_dataset_table = evaluation_main[
        [
            "dataset",
            "method",
            "ndcg_at_10",
            "recall_at_20",
            "dense_depth",
            "sparse_depth",
            "sparse_support",
            "sparse_exhaustion_rate",
            "fallback_rate",
        ]
    ].sort_values(["dataset", "method"])
    mechanism_macro = macro[
        macro["method"].isin(("original", "dense_only", "sparse_only", "proposed"))
    ]

    fidelity = summary[
        summary["dataset"].isin(FIDELITY_DATASETS) & (summary["track"] == "fidelity")
    ]
    fidelity_macro = (
        fidelity.groupby("method", as_index=False)[list(PRIMARY_METRICS)]
        .mean()
        .sort_values("method")
    )
    fidelity_macro.insert(0, "source", "published_prompt_and_integration")
    own_complete_methods = macro[macro["method"].isin(("original", "proposed"))].copy()
    own_complete_methods.insert(0, "source", "frozen_primary_protocol")
    complete_method_comparison = pd.concat(
        [own_complete_methods, fidelity_macro], ignore_index=True
    )

    reference_sensitivity = summary[
        summary["dataset"].isin(EVALUATION_DATASETS)
        & summary["track"].isin(("controlled", "ablation"))
        & (summary["condition_id"] == "primary")
        & (summary["method"] == "proposed")
        & (summary["rrf_constant"] == 60)
        & summary["reference_count"].isin((1, 3, 5))
    ]
    reference_macro = (
        reference_sensitivity.groupby("reference_count", as_index=False)[
            list(PRIMARY_METRICS)
        ]
        .mean()
        .sort_values("reference_count")
    )

    rrf_sensitivity = summary[
        summary["dataset"].isin(EVALUATION_DATASETS)
        & summary["track"].isin(("controlled", "ablation"))
        & (summary["condition_id"] == "primary")
        & (summary["method"] == "proposed")
        & (summary["reference_count"] == 5)
        & summary["rrf_constant"].isin((2, 20, 60, 100))
    ]
    rrf_macro = (
        rrf_sensitivity.groupby("rrf_constant", as_index=False)[list(PRIMARY_METRICS)]
        .mean()
        .sort_values("rrf_constant")
    )

    sparse_operator_macro = macro[
        macro["method"].isin(
            ("proposed", "sparse_boolean_mask", "sparse_references_only")
        )
    ]

    fixed_macro = pd.DataFrame()
    if not fixed_summary.empty:
        fixed_macro = (
            fixed_summary[
                fixed_summary["dataset"].isin(EVALUATION_DATASETS)
                & (fixed_summary["condition_id"] == "primary")
                & (fixed_summary["reference_count"] == 5)
                & (fixed_summary["rrf_constant"] == 60)
                & fixed_summary["method"].isin(
                    ("original", "bridge_shared", "proposed")
                )
            ]
            .groupby(["method", "top_l"], as_index=False)[
                ["ndcg_at_10", "recall_at_20", "complete_top20_exact_rate"]
            ]
            .mean()
            .sort_values(["method", "top_l"])
        )

    robustness = summary[
        summary["dataset"].isin(EVALUATION_DATASETS)
        & (summary["track"] == "robustness")
        & summary["method"].isin(("original", "proposed"))
    ]
    robustness_pairs = _original_proposed_pairs(
        robustness, group_columns=("condition_id", "dataset")
    )
    negative_robustness = robustness_pairs[
        (robustness_pairs["dense_reduction_pct"] < 0.0)
        | (robustness_pairs["sparse_reduction_pct"] < 0.0)
    ] if not robustness_pairs.empty else robustness_pairs
    if negative_robustness.empty:
        negative_robustness_text = "未观察到 Proposed 相对 Original 的访问深度恶化。"
    else:
        cells = [
            (
                f"{row.condition_id}/{row.dataset}：Dense {row.dense_reduction_pct:.2f}%，"
                f"Sparse {row.sparse_reduction_pct:.2f}%"
            )
            for row in negative_robustness.itertuples(index=False)
        ]
        negative_robustness_text = (
            "以下条件出现访问深度恶化（负百分比表示读取更多）：" + "；".join(cells) + "。"
        )

    scale = summary[
        (summary["track"] == "scale")
        & summary["method"].isin(("original", "proposed"))
    ]
    scale_pairs = _original_proposed_pairs(scale, group_columns=("dataset",))
    if not scale_pairs.empty:
        scale_pairs.insert(
            1,
            "documents",
            scale_pairs["dataset"].str.rsplit("-", n=1).str[-1].astype(int),
        )
        scale_pairs = scale_pairs.sort_values("documents")

    unique_queries = query_means[["dataset", "query_id"]].drop_duplicates().shape[0]
    lines = [
        "# 正式实验结果报告",
        "",
        (
            "> 本报告只读取真实逐查询记录；七个正式数据集等权汇总，"
            "鲁棒性与规模实验按 track 单独报告。"
        ),
        "",
        "## 数据完整性",
        "",
        f"- 逐查询×方法×生成重复结果：{len(frame):,} 条",
        f"- 独立查询单元：{unique_queries:,} 条",
        f"- 数据集：{frame['dataset'].nunique()} 个",
        f"- 方法：{frame['method'].nunique()} 个",
        f"- 生成失败回退率：{frame['fallback'].mean():.4%}",
        "",
        "## Controlled 主结果（数据集等权）",
        "",
        macro.to_markdown(index=False, floatfmt=".4f"),
        "",
        "### 主结果的查询级分层 bootstrap 95% 区间",
        "",
        method_intervals.to_markdown(index=False, floatfmt=".4f"),
        "",
        "## 七个正式数据集主结果",
        "",
        _markdown_or_empty(main_dataset_table),
        "",
        "## 2×2 机制实验（数据集等权）",
        "",
        _markdown_or_empty(mechanism_macro),
        "",
        "## 相对 Original 的访问变化",
        "",
        access.to_markdown(index=False, floatfmt=".3f"),
        "",
        "### 数据集等权访问变化及 95% 区间",
        "",
        access_intervals.to_markdown(index=False, floatfmt=".4f"),
        "",
        "## 主比较",
        "",
        tests.to_markdown(index=False, floatfmt=".6f"),
        "",
        "### 结论分类",
        "",
        classifications.to_markdown(index=False),
        "",
        "## 公开方法完整复现",
        "",
        (
            "下表将各论文对应的提示词与整合规则同冻结的 Original 和 Proposed "
            "并列展示；该表为描述性完整方法比较，预注册显著性检验仍只针对 "
            "controlled 主比较。"
        ),
        "",
        _markdown_or_empty(complete_method_comparison),
        "",
        "## 消融与敏感性",
        "",
        "### 参考文本数量",
        "",
        _markdown_or_empty(reference_macro),
        "",
        "### Sparse 算子",
        "",
        _markdown_or_empty(sparse_operator_macro),
        "",
        "### RRF 常数",
        "",
        _markdown_or_empty(rrf_macro),
        "",
        "### 固定 Top-L",
        "",
        _markdown_or_empty(fixed_macro),
        "",
        "## 鲁棒性：第二生成模型与第二 Dense 编码器",
        "",
        _markdown_or_empty(robustness_pairs),
        "",
        negative_robustness_text,
        "",
        "## 规模趋势",
        "",
        _markdown_or_empty(scale_pairs),
        "",
        "## 生成成本",
        "",
        (
            generation_summary.to_markdown(index=False, floatfmt=".3f")
            if not generation_summary.empty
            else "尚无可汇总的生成记录。"
        ),
        "",
        "## 结论边界",
        "",
        "逻辑访问深度不等同于在线延迟；生成成本、表示构造、检索执行和融合回放分别核算。完整结果保留每个数据集与失败回退记录，不以总体均值隐藏混合或负面结果。",
    ]
    report_path = output_directory / "REPORT.md"
    atomic_write_text(report_path, "\n".join(lines) + "\n")
    return report_path
