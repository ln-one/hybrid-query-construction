from __future__ import annotations

import json
import sys
from pathlib import Path

import matplotlib
import numpy as np
import pandas as pd
from matplotlib.colors import ListedColormap

matplotlib.use("Agg")
import matplotlib.pyplot as plt

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "figures"))

from qudar_style import COLORS, apply_style, save_figure  # noqa: E402

DATASETS = (
    "scifact",
    "nfcorpus",
    "trec-covid",
    "fiqa",
    "arguana",
    "webis-touche2020",
    "scidocs",
)
RAW = ROOT / "artifacts" / "results" / "raw"
CATEGORIES = ("Loss", "Tie", "Gain")
TOP_L = 50


def _read_rows(path: Path) -> list[dict[str, object]]:
    return [json.loads(line) for line in path.read_text().splitlines()]


def _load_results(*, fixed: bool) -> pd.DataFrame:
    rows: list[dict[str, object]] = []
    suffix = "-fixed-top-l" if fixed else ""
    for dataset in DATASETS:
        rows.extend(_read_rows(RAW / f"{dataset}{suffix}.jsonl"))
    frame = pd.DataFrame(rows)
    selected = (
        (frame["track"] == "controlled")
        & (frame["condition_id"] == "primary")
        & (frame["reference_count"] == 5)
        & (frame["rrf_constant"] == 60)
        & frame["method"].isin(("original", "proposed"))
    )
    if fixed:
        selected &= frame["top_l"] == TOP_L
    return frame[selected]


def _judgment(values: pd.Series) -> pd.Series:
    return pd.Series(
        np.where(values > 1e-12, "Gain", np.where(values < -1e-12, "Loss", "Tie")),
        index=values.index,
    )


def _transition_matrix(metric: str) -> np.ndarray:
    key = ["dataset", "query_id", "draw_id"]
    complete = _load_results(fixed=False).pivot(
        index=key, columns="method", values=metric
    )
    fixed = _load_results(fixed=True).pivot(
        index=key, columns="method", values=metric
    )
    labels = pd.DataFrame(index=complete.index)
    labels["complete"] = _judgment(
        complete["proposed"] - complete["original"]
    )
    labels["fixed"] = _judgment(fixed["proposed"] - fixed["original"])
    labels = labels.reset_index()

    matrices: list[pd.DataFrame] = []
    for _, dataset in labels.groupby("dataset"):
        matrix = pd.crosstab(
            dataset["fixed"], dataset["complete"], normalize="all"
        ).reindex(index=CATEGORIES, columns=CATEGORIES, fill_value=0.0)
        matrices.append(matrix)
    return (sum(matrices) / len(matrices)).to_numpy() * 100.0


def _draw_matrix(axis: plt.Axes, values: np.ndarray, title: str) -> None:
    semantic_cells = np.ones((3, 3), dtype=int)
    np.fill_diagonal(semantic_cells, 0)
    semantic_cells[0, 2] = 2
    semantic_cells[2, 0] = 2
    cmap = ListedColormap(("#EEF1F3", "#D7F0E9", "#F4D8D2"))
    axis.imshow(semantic_cells, cmap=cmap, vmin=0, vmax=2, aspect="equal")

    for row in range(3):
        for column in range(3):
            axis.text(
                column,
                row,
                f"{values[row, column]:.2f}",
                ha="center",
                va="center",
                color=COLORS["ink"],
                fontsize=6.5,
                fontweight="bold" if row != column else "normal",
            )

    changed = values.sum() - np.trace(values)
    reversed_ = values[0, 2] + values[2, 0]
    axis.set_title(title, pad=14.0)
    axis.text(
        0.5,
        1.035,
        f"changed {changed:.2f}%  ·  reversed {reversed_:.2f}%",
        transform=axis.transAxes,
        ha="center",
        va="bottom",
        fontsize=5.8,
        color=COLORS["ink"],
    )
    axis.set_xticks(range(3), CATEGORIES)
    axis.set_yticks(range(3), CATEGORIES)
    axis.set_xlabel("Complete-list judgment")
    axis.tick_params(length=0, pad=1.5)
    axis.set_xticks(np.arange(-0.5, 3, 1), minor=True)
    axis.set_yticks(np.arange(-0.5, 3, 1), minor=True)
    axis.grid(which="minor", color="white", linewidth=1.2)
    axis.grid(which="major", visible=False)
    axis.tick_params(which="minor", bottom=False, left=False)
    for spine in axis.spines.values():
        spine.set_color(COLORS["ink"])
        spine.set_linewidth(0.6)


def main() -> None:
    apply_style()
    ndcg = _transition_matrix("ndcg_at_10")
    recall = _transition_matrix("recall_at_20")

    fig, axes = plt.subplots(1, 2, figsize=(3.35, 1.75))
    _draw_matrix(axes[0], ndcg, "(a) nDCG@10")
    _draw_matrix(axes[1], recall, "(b) Recall@20")
    axes[0].set_ylabel(f"Fixed-$L$ judgment ($L={TOP_L}$)")
    axes[1].set_yticklabels([])
    fig.subplots_adjust(left=0.15, right=0.995, bottom=0.23, top=0.80, wspace=0.26)
    save_figure(fig, Path(__file__), "fig_fixed_top_l_diagnostics.pdf")
    plt.close(fig)


if __name__ == "__main__":
    main()
