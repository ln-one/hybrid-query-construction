from __future__ import annotations

from pathlib import Path
from typing import Any

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from .io import atomic_write_text, read_jsonl
from .statistics import holm_adjust, stratified_macro_bootstrap, stratified_sign_flip_pvalue

PRIMARY_METRICS = ("ndcg_at_10", "recall_at_20", "dense_depth", "sparse_depth")
COMPARATORS = ("original", "bridge_shared")


def load_result_rows(input_directory: Path) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for path in sorted(input_directory.rglob("*.jsonl")):
        if "fixed-top-l" not in path.name:
            rows.extend(read_jsonl(path))
    return rows


def _query_means(frame: pd.DataFrame) -> pd.DataFrame:
    return (
        frame.groupby(
            [
                "dataset",
                "query_id",
                "track",
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
            ["dataset", "track", "reference_count", "rrf_constant", "method", "query_id"]
        )
    )


def _summary(query_means: pd.DataFrame) -> pd.DataFrame:
    return (
        query_means.groupby(
            ["dataset", "track", "method", "reference_count", "rrf_constant"],
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
        .sort_values(["dataset", "track", "reference_count", "rrf_constant", "method"])
    )


def _access_changes(query_means: pd.DataFrame) -> pd.DataFrame:
    controlled = query_means[
        (query_means["track"] == "controlled")
        & (query_means["reference_count"] == 5)
        & (query_means["rrf_constant"] == 60)
    ]
    rows: list[dict[str, object]] = []
    for dataset, data in controlled.groupby("dataset"):
        original = data[data["method"] == "original"].set_index("query_id")
        for method, method_data in data.groupby("method"):
            current = method_data.set_index("query_id")
            common = original.index.intersection(current.index)
            if common.empty:
                continue
            dense_original = original.loc[common, "dense_depth"].to_numpy(float)
            sparse_original = original.loc[common, "sparse_depth"].to_numpy(float)
            dense_current = current.loc[common, "dense_depth"].to_numpy(float)
            sparse_current = current.loc[common, "sparse_depth"].to_numpy(float)
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
    return pd.DataFrame(rows).sort_values(["dataset", "method"])


def _paired_tests(query_means: pd.DataFrame) -> pd.DataFrame:
    controlled = query_means[
        (query_means["track"] == "controlled")
        & (query_means["reference_count"] == 5)
        & (query_means["rrf_constant"] == 60)
    ]
    proposed = controlled[controlled["method"] == "proposed"]
    rows: list[dict[str, object]] = []
    pvalues: dict[str, float] = {}
    for comparator in COMPARATORS:
        baseline = controlled[controlled["method"] == comparator]
        paired = proposed.merge(
            baseline,
            on=["dataset", "query_id"],
            suffixes=("_proposed", "_comparator"),
            validate="one_to_one",
        )
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
            name = f"{comparator}:{metric}"
            pvalue = stratified_sign_flip_pvalue(differences)
            pvalues[name] = pvalue
            rows.append(
                {
                    "comparison": f"proposed_vs_{comparator}",
                    "metric": metric,
                    "favorable_difference": estimate,
                    "ci95_lower": lower,
                    "ci95_upper": upper,
                    "p_raw": pvalue,
                }
            )
    adjusted = holm_adjust(pvalues)
    for row in rows:
        key = f"{str(row['comparison']).removeprefix('proposed_vs_')}:{row['metric']}"
        row["p_holm"] = adjusted[key]
    return pd.DataFrame(rows)


def _plot_quality_access(summary: pd.DataFrame, output: Path) -> None:
    controlled = summary[
        (summary["track"] == "controlled")
        & (summary["reference_count"] == 5)
        & (summary["rrf_constant"] == 60)
    ]
    macro = controlled.groupby("method", as_index=False)[
        ["ndcg_at_10", "dense_depth", "sparse_depth"]
    ].mean()
    fig, axis = plt.subplots(figsize=(7.2, 4.8))
    access = macro["dense_depth"] + macro["sparse_depth"]
    axis.scatter(access, macro["ndcg_at_10"], color="#0072B2", s=45)
    for _, row in macro.iterrows():
        axis.annotate(
            row["method"],
            (row["dense_depth"] + row["sparse_depth"], row["ndcg_at_10"]),
            xytext=(4, 4),
            textcoords="offset points",
            fontsize=8,
        )
    axis.set_xlabel("Mean logical access (Dense + Sparse)")
    axis.set_ylabel("Dataset-macro nDCG@10")
    axis.grid(alpha=0.2)
    fig.tight_layout()
    fig.savefig(output, dpi=220)
    plt.close(fig)


def build_report(input_directory: Path, output_directory: Path) -> Path:
    rows = load_result_rows(input_directory)
    if not rows:
        raise RuntimeError("no real per-query result records found")
    output_directory.mkdir(parents=True, exist_ok=True)
    frame = pd.DataFrame(rows)
    query_means = _query_means(frame)
    summary = _summary(query_means)
    access = _access_changes(query_means)
    tests = _paired_tests(query_means)

    query_means.to_csv(output_directory / "per-query-draw-mean.csv", index=False)
    summary.to_csv(output_directory / "main-results.csv", index=False)
    access.to_csv(output_directory / "access-changes-vs-original.csv", index=False)
    tests.to_csv(output_directory / "primary-paired-tests.csv", index=False)
    _plot_quality_access(summary, output_directory / "quality-access.png")

    controlled = summary[
        (summary["track"] == "controlled")
        & (summary["reference_count"] == 5)
        & (summary["rrf_constant"] == 60)
    ]
    macro = (
        controlled.groupby("method", as_index=False)[list(PRIMARY_METRICS)]
        .mean()
        .sort_values("method")
    )
    unique_queries = query_means[["dataset", "query_id"]].drop_duplicates().shape[0]
    lines = [
        "# 正式实验结果报告",
        "",
        "> 本报告只读取真实逐查询记录；开发、held-out、鲁棒性与规模结果必须按 track 分开解释。",
        "",
        "## 数据完整性",
        "",
        f"- 逐查询×生成记录：{len(frame):,} 条",
        f"- 独立查询单元：{unique_queries:,} 条",
        f"- 数据集：{frame['dataset'].nunique()} 个",
        f"- 方法：{frame['method'].nunique()} 个",
        f"- 生成失败回退率：{frame['fallback'].mean():.4%}",
        "",
        "## Controlled 主结果（数据集等权）",
        "",
        macro.to_markdown(index=False, floatfmt=".4f"),
        "",
        "## 相对 Original 的访问变化",
        "",
        access.to_markdown(index=False, floatfmt=".3f"),
        "",
        "## 预注册主比较",
        "",
        tests.to_markdown(index=False, floatfmt=".6f"),
        "",
        "## 结论边界",
        "",
        "逻辑访问深度不等同于在线延迟；生成成本、表示构造、检索执行和融合回放分别核算。完整结果保留每个数据集与失败回退记录，不以总体均值隐藏混合或负面结果。",
    ]
    report_path = output_directory / "REPORT.md"
    atomic_write_text(report_path, "\n".join(lines) + "\n")
    return report_path
