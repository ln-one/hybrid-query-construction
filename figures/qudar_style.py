from __future__ import annotations

from pathlib import Path

import matplotlib.pyplot as plt

COLORS = {
    "original": "#9AA3AD",
    "shared": "#90C8F8",
    "dense": "#5068C8",
    "sparse": "#A8E850",
    "desa": "#30B088",
    "qudar": "#98A0E0",
    "accent": "#F0B928",
    "negative": "#D98273",
    "ink": "#263238",
    "grid": "#D9DEE3",
}

MARKERS = {
    "original": "o",
    "shared": "s",
    "dense": "^",
    "sparse": "v",
    "desa": "D",
    "qudar": "P",
}


def apply_style() -> None:
    """Apply a compact serif style inspired by QuDAR's ACL figures."""
    plt.rcParams.update(
        {
            "font.family": "serif",
            "font.serif": ["Times New Roman", "Nimbus Roman", "STIXGeneral", "DejaVu Serif"],
            "pdf.fonttype": 42,
            "ps.fonttype": 42,
            "mathtext.fontset": "stix",
            "font.size": 7.5,
            "axes.titlesize": 8.3,
            "axes.titleweight": "regular",
            "axes.labelsize": 7.8,
            "axes.labelcolor": COLORS["ink"],
            "axes.edgecolor": COLORS["ink"],
            "axes.linewidth": 0.65,
            "axes.grid": True,
            "axes.axisbelow": True,
            "grid.color": COLORS["grid"],
            "grid.linestyle": (0, (2.0, 2.0)),
            "grid.linewidth": 0.45,
            "grid.alpha": 0.9,
            "xtick.labelsize": 6.9,
            "ytick.labelsize": 6.9,
            "xtick.color": COLORS["ink"],
            "ytick.color": COLORS["ink"],
            "xtick.major.width": 0.55,
            "ytick.major.width": 0.55,
            "xtick.major.size": 2.6,
            "ytick.major.size": 2.6,
            "legend.fontsize": 6.8,
            "legend.frameon": False,
            "lines.linewidth": 1.25,
            "lines.markersize": 3.8,
            "savefig.dpi": 450,
            "savefig.bbox": "tight",
            "savefig.pad_inches": 0.025,
            "figure.facecolor": "white",
            "axes.facecolor": "white",
        }
    )


def finish_axis(axis: plt.Axes) -> None:
    for spine in axis.spines.values():
        spine.set_visible(True)
        spine.set_color(COLORS["ink"])
        spine.set_linewidth(0.65)
    axis.tick_params(direction="out", pad=1.8)


def save_figure(
    figure: plt.Figure,
    script_path: Path,
    paper_filename: str,
) -> None:
    stem = script_path.resolve().parent / script_path.stem
    figure.savefig(stem.with_suffix(".png"), dpi=450)
    figure.savefig(stem.with_suffix(".svg"))
    figure.savefig(stem.with_suffix(".pdf"))

    root = script_path.resolve().parents[2]
    paper_output = root / "paper" / "acl2027" / "figures"
    paper_output.mkdir(parents=True, exist_ok=True)
    figure.savefig(paper_output / paper_filename)
