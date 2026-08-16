from __future__ import annotations

import sys
from pathlib import Path

import matplotlib
import pandas as pd

matplotlib.use("Agg")
import matplotlib.pyplot as plt

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "figures"))

from qudar_style import COLORS, MARKERS, apply_style, finish_axis, save_figure


RESULTS = ROOT / "report" / "main-results.csv"
QUDAR = ROOT / "report" / "qudar-baseline-results.csv"

METHODS = (
    ("original", "Original", "original"),
    ("bridge_shared", "Shared", "shared"),
    ("dense_only", "Dense only", "dense"),
    ("sparse_only", "Sparse only", "sparse"),
    ("proposed", "DESA", "desa"),
)


def _macro_results() -> pd.DataFrame:
    frame = pd.read_csv(RESULTS)
    macro = (
        frame.groupby("method", as_index=False)[
            ["ndcg_at_10", "recall_at_20", "dense_depth", "sparse_depth"]
        ]
        .mean()
        .set_index("method")
    )
    macro["total_depth"] = macro["dense_depth"] + macro["sparse_depth"]
    original_depth = float(macro.loc["original", "total_depth"])
    qudar = pd.read_csv(QUDAR)
    qudar_macro = qudar[qudar["method"] == "qudar_simple_rrf_matched"][
        ["ndcg_at_10", "recall_at_20"]
    ].mean()
    macro.loc["qudar_simple_rrf_matched", "ndcg_at_10"] = qudar_macro["ndcg_at_10"]
    macro.loc["qudar_simple_rrf_matched", "recall_at_20"] = qudar_macro[
        "recall_at_20"
    ]
    macro.loc["qudar_simple_rrf_matched", "total_depth"] = 4000.0
    return macro


def main() -> None:
    apply_style()
    macro = _macro_results()
    fig, axis = plt.subplots(figsize=(3.35, 2.28))
    plot_methods = (*METHODS, ("qudar_simple_rrf_matched", "QuDAR-simple", "qudar"))

    metric = "ndcg_at_10"
    original_value = float(macro.loc["original", metric])
    original_depth = float(macro.loc["original", "total_depth"])
    axis.axvspan(800, original_depth, color=COLORS["desa"], alpha=0.045, zorder=0)
    axis.axvline(
        original_depth,
        color=COLORS["original"],
        linewidth=0.75,
        linestyle=(0, (3, 2)),
    )
    axis.axhline(
        original_value,
        color=COLORS["original"],
        linewidth=0.75,
        linestyle=(0, (3, 2)),
    )
    for method, label, style_key in plot_methods:
        axis.scatter(
            macro.loc[method, "total_depth"],
            macro.loc[method, metric],
            s=27 if style_key == "desa" else 21,
            marker=MARKERS[style_key],
            facecolor=COLORS[style_key],
            edgecolor="white",
            linewidth=0.4,
            zorder=3,
            label=label,
        )
    axis.set_ylabel("nDCG@10")
    axis.set_xlim(800, 4200)
    axis.set_xlabel("Mean accessed rank entries (lower is better)")
    finish_axis(axis)

    handles, labels = axis.get_legend_handles_labels()
    fig.legend(
        handles,
        labels,
        loc="upper center",
        bbox_to_anchor=(0.5, 0.985),
        ncol=3,
        fontsize=5.9,
        handletextpad=0.25,
        columnspacing=0.75,
    )
    fig.subplots_adjust(left=0.16, right=0.99, bottom=0.20, top=0.79)
    save_figure(fig, Path(__file__), "fig_quality_access_tradeoff.pdf")
    plt.close(fig)


if __name__ == "__main__":
    main()
