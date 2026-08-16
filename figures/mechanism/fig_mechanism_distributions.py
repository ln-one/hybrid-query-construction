from __future__ import annotations

import sys
from pathlib import Path

import matplotlib
import numpy as np
import pandas as pd

matplotlib.use("Agg")
import matplotlib.pyplot as plt

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "figures"))

from qudar_style import COLORS, apply_style, finish_axis, save_figure

DATA = ROOT / "figures" / "data" / "mechanism-distributions.csv"
ORDER = (
    "scifact",
    "nfcorpus",
    "trec-covid",
    "fiqa",
    "arguana",
    "webis-touche2020",
    "scidocs",
)
LABELS = ("SciFact", "NFCorpus", "TREC-C", "FiQA", "ArguAna", "Touché", "SCIDOCS")


def _boxplot(axis: plt.Axes, values: list[np.ndarray], color: str) -> None:
    plot = axis.boxplot(
        values,
        patch_artist=True,
        showfliers=False,
        widths=0.62,
        medianprops={"color": "#222222", "linewidth": 1.1},
        whiskerprops={"color": "#666666", "linewidth": 0.8},
        capprops={"color": "#666666", "linewidth": 0.8},
    )
    for box in plot["boxes"]:
        box.set(facecolor=color, edgecolor=color, alpha=0.62, linewidth=0.8)


def main() -> None:
    apply_style()
    frame = pd.read_csv(DATA, dtype={"query_id": str})
    fig, axes = plt.subplots(1, 2, figsize=(3.35, 1.82))
    angle = [
        frame.loc[frame["dataset"] == dataset, "dense_angle_degrees"].to_numpy()
        for dataset in ORDER
    ]
    turnover = [
        100.0
        * frame.loc[frame["dataset"] == dataset, "sparse_top20_turnover"].to_numpy()
        for dataset in ORDER
    ]
    _boxplot(axes[0], angle, COLORS["dense"])
    _boxplot(axes[1], turnover, COLORS["sparse"])
    axes[0].axhline(
        45.0,
        color=COLORS["accent"],
        linestyle="--",
        linewidth=1.0,
        label="45° bound",
    )
    axes[0].set_ylabel("Dense angle (degrees)")
    axes[0].set_title("(a) Dense residual")
    axes[0].legend(frameon=False, fontsize=5.8, loc="upper right")
    axes[1].set_ylabel("Sparse Top-20 turnover (%)")
    axes[1].set_title("(b) Sparse anchoring")
    for axis in axes:
        axis.set_xticks(range(1, len(LABELS) + 1), LABELS, rotation=42, ha="right")
        finish_axis(axis)
    fig.subplots_adjust(left=0.14, right=0.995, bottom=0.31, top=0.88, wspace=0.38)
    save_figure(fig, Path(__file__), "fig_mechanism_distributions.pdf")
    plt.close(fig)


if __name__ == "__main__":
    main()
