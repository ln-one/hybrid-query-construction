from __future__ import annotations

from collections.abc import Sequence

import numpy as np
import pandas as pd

from .fusion import complete_wrrf
from .statistics import (
    holm_adjust,
    stratified_macro_bootstrap,
    stratified_sign_flip_pvalue,
)


def qudar_simple_rrf(
    rankings: Sequence[Sequence[str]],
    *,
    retrieval_depth: int = 1000,
    top_k: int = 20,
    constant: int = 60,
) -> list[str]:
    """Reproduce QuDAR-simple RRF over four matched retrieval signals."""
    if len(rankings) != 4:
        raise ValueError("QuDAR-simple RRF requires exactly four rankings")
    if retrieval_depth <= 0:
        raise ValueError("retrieval_depth must be positive")
    return complete_wrrf(
        [ranking[:retrieval_depth] for ranking in rankings],
        top_k=top_k,
        constant=constant,
    )


def fixed_cutoff_diagnostics(
    complete: pd.DataFrame,
    fixed: pd.DataFrame,
    *,
    methods: Sequence[str],
) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Summarize query-level disagreement with complete-list fusion."""
    key = [
        "dataset",
        "query_id",
        "draw_id",
        "method",
        "reference_count",
        "rrf_constant",
    ]
    selected_complete = complete[complete["method"].isin(methods)]
    selected_fixed = fixed[fixed["method"].isin(methods)]
    merged = selected_fixed.merge(
        selected_complete[[*key, "ndcg_at_10", "recall_at_20"]],
        on=key,
        suffixes=("_fixed", "_complete"),
        validate="many_to_one",
    )
    for metric in ("ndcg_at_10", "recall_at_20"):
        difference = merged[f"{metric}_fixed"] - merged[f"{metric}_complete"]
        merged[f"{metric}_changed"] = difference.abs() > 1e-12
        merged[f"{metric}_abs_error"] = difference.abs()

    diagnostic_columns = [
        "complete_top20_exact",
        "ndcg_at_10_changed",
        "recall_at_20_changed",
        "ndcg_at_10_abs_error",
        "recall_at_20_abs_error",
    ]
    by_dataset = merged.groupby(
        ["dataset", "method", "top_l"], as_index=False
    )[diagnostic_columns].mean()
    diagnostics = by_dataset.groupby(["method", "top_l"], as_index=False)[
        diagnostic_columns
    ].mean()

    original_fixed = selected_fixed[selected_fixed["method"] == "original"][
        [
            "dataset",
            "query_id",
            "draw_id",
            "top_l",
            "ndcg_at_10",
            "recall_at_20",
        ]
    ].rename(
        columns={
            "ndcg_at_10": "original_fixed_ndcg",
            "recall_at_20": "original_fixed_recall",
        }
    )
    original_complete = selected_complete[
        selected_complete["method"] == "original"
    ][["dataset", "query_id", "draw_id", "ndcg_at_10", "recall_at_20"]].rename(
        columns={
            "ndcg_at_10": "original_complete_ndcg",
            "recall_at_20": "original_complete_recall",
        }
    )
    compared_fixed = selected_fixed[selected_fixed["method"] != "original"][
        [
            "dataset",
            "query_id",
            "draw_id",
            "method",
            "top_l",
            "ndcg_at_10",
            "recall_at_20",
        ]
    ].rename(
        columns={"ndcg_at_10": "fixed_ndcg", "recall_at_20": "fixed_recall"}
    )
    compared_complete = selected_complete[
        selected_complete["method"] != "original"
    ][["dataset", "query_id", "draw_id", "method", "ndcg_at_10", "recall_at_20"]].rename(
        columns={
            "ndcg_at_10": "complete_ndcg",
            "recall_at_20": "complete_recall",
        }
    )
    comparisons = (
        compared_fixed.merge(
            original_fixed,
            on=["dataset", "query_id", "draw_id", "top_l"],
            validate="many_to_one",
        )
        .merge(
            compared_complete,
            on=["dataset", "query_id", "draw_id", "method"],
            validate="many_to_one",
        )
        .merge(
            original_complete,
            on=["dataset", "query_id", "draw_id"],
            validate="many_to_one",
        )
    )
    conclusion_columns: list[str] = []
    for metric in ("ndcg", "recall"):
        fixed_delta = (
            comparisons[f"fixed_{metric}"]
            - comparisons[f"original_fixed_{metric}"]
        )
        complete_delta = (
            comparisons[f"complete_{metric}"]
            - comparisons[f"original_complete_{metric}"]
        )
        change = f"{metric}_conclusion_change"
        reversal = f"{metric}_direction_reversal"
        comparisons[change] = np.sign(fixed_delta) != np.sign(complete_delta)
        comparisons[reversal] = fixed_delta * complete_delta < 0.0
        conclusion_columns.extend((change, reversal))
    conclusion_by_dataset = comparisons.groupby(
        ["dataset", "method", "top_l"], as_index=False
    )[conclusion_columns].mean()
    conclusions = conclusion_by_dataset.groupby(
        ["method", "top_l"], as_index=False
    )[conclusion_columns].mean()
    return diagnostics, conclusions


def paired_quality_tests(
    frame: pd.DataFrame,
    *,
    proposed: str,
    comparator: str,
) -> pd.DataFrame:
    """Run equal-dataset paired tests after averaging draws within query."""
    metrics = ["ndcg_at_10", "recall_at_20"]
    query_means = frame.groupby(
        ["dataset", "query_id", "method"], as_index=False
    )[metrics].mean()
    left = query_means[query_means["method"] == proposed]
    right = query_means[query_means["method"] == comparator]
    paired = left.merge(
        right,
        on=["dataset", "query_id"],
        suffixes=("_proposed", "_comparator"),
        validate="one_to_one",
    )
    rows: list[dict[str, object]] = []
    pvalues: dict[str, float] = {}
    for metric in metrics:
        favorable = paired[f"{metric}_proposed"] - paired[f"{metric}_comparator"]
        differences = {
            str(dataset): values.to_list()
            for dataset, values in favorable.groupby(paired["dataset"])
        }
        estimate, lower, upper = stratified_macro_bootstrap(differences)
        pvalue = stratified_sign_flip_pvalue(differences)
        pvalues[metric] = pvalue
        rows.append(
            {
                "comparison": f"{proposed}_vs_{comparator}",
                "metric": metric,
                "favorable_difference": estimate,
                "ci95_lower": lower,
                "ci95_upper": upper,
                "p_raw": pvalue,
            }
        )
    adjusted = holm_adjust(pvalues)
    for row in rows:
        row["p_holm"] = adjusted[str(row["metric"])]
    return pd.DataFrame(rows)
