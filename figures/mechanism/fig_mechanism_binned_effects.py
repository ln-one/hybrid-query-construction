from __future__ import annotations

import sys
from pathlib import Path

import matplotlib
import pandas as pd

matplotlib.use("Agg")
import matplotlib.pyplot as plt

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "figures"))

from qudar_style import COLORS, apply_style, finish_axis, save_figure

DATA = ROOT / "figures" / "data" / "mechanism-binned-effects.csv"


def main() -> None:
    apply_style()
    frame = pd.read_csv(DATA)
    frame = frame[frame["dataset"] == "macro_equal_dataset"]
    fig, axes = plt.subplots(2, 2, figsize=(7.0, 4.65), sharex="col")
    specifications = (
        ("dense", "delta_ndcg", axes[0, 0], "(a) Dense-only quality", "Δ nDCG@10"),
        (
            "dense",
            "depth_reduction_pct",
            axes[1, 0],
            "(c) Dense-only access",
            "Dense depth reduction (%)",
        ),
        ("sparse", "delta_ndcg", axes[0, 1], "(b) Sparse-only quality", "Δ nDCG@10"),
        (
            "sparse",
            "depth_reduction_pct",
            axes[1, 1],
            "(d) Sparse-only access",
            "Sparse depth reduction (%)",
        ),
    )
    for mechanism, metric, axis, title, ylabel in specifications:
        data = frame[frame["mechanism"] == mechanism].sort_values("bin")
        axis.plot(
            data["bin"],
            data[metric],
            color=COLORS[mechanism],
            marker="o",
            markersize=4.5,
            linewidth=1.5,
        )
        axis.axhline(0.0, color=COLORS["ink"], linewidth=0.7)
        axis.set_title(title)
        axis.set_ylabel(ylabel)
        finish_axis(axis)
    axes[1, 0].set_xlabel("Dense angle quartile")
    axes[1, 1].set_xlabel("Sparse turnover quartile")
    for axis in axes.flat:
        axis.set_xticks((1, 2, 3, 4))
    fig.tight_layout(w_pad=2.0, h_pad=1.3)
    save_figure(fig, Path(__file__), "fig_mechanism_binned_effects.pdf")
    plt.close(fig)


if __name__ == "__main__":
    main()
