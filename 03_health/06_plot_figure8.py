#!/usr/bin/env python3
"""Render main-text Figure 8 from the Nature Communications Source Data."""

from __future__ import annotations

import argparse
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
import numpy as np
import pandas as pd

COLORS = {"Category 2": "#0072B2", "Category 3": "#FD8D3C", "Category 4": "#E31A1C"}
OFFSETS = {"Category 2": 0.22, "Category 3": 0.0, "Category 4": -0.22}
X_MAX = 4.0
def arguments() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source-data", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    return parser.parse_args()


def read_sheets(path: Path) -> tuple[pd.DataFrame, pd.DataFrame]:
    a = pd.read_excel(path, sheet_name="Fig. 8a", header=0)
    b = pd.read_excel(path, sheet_name="Fig. 8b", header=0)
    required = {"Row_label", "Category", "Point_type", "RR", "CI_low", "CI_high", "n_sites"}
    for name, frame in (("Figure 8a", a), ("Figure 8b", b)):
        missing = required - set(frame.columns)
        if missing:
            raise ValueError(f"{name} is missing columns: {sorted(missing)}")
        if frame[["RR", "CI_low", "CI_high"]].isna().any().any():
            raise ValueError(f"{name} contains missing RR or confidence limits")
        if not ((frame.CI_low <= frame.RR) & (frame.RR <= frame.CI_high)).all():
            raise ValueError(f"{name} contains an RR outside its confidence interval")
    if len(a) != 25 or len(b) != 6 or not (b.n_sites == 3).all():
        raise ValueError("Figure 8 row counts or panel-b contributing-city counts are unexpected")
    return a, b


def draw(ax, row, y: float, marker: str, size: float) -> None:
    rr, low, high = float(row.RR), float(row.CI_low), float(row.CI_high)
    shown_high = min(high, X_MAX)
    color = COLORS[row.Category]
    ax.errorbar(rr, y, xerr=np.array([[rr - low], [shown_high - rr]]), fmt=marker,
                color=color, markerfacecolor=color, markeredgecolor=color,
                markersize=size, linewidth=1, elinewidth=1, capsize=2.2,
                capthick=1, clip_on=True, zorder=4)
    if high > X_MAX:
        ax.plot(X_MAX, y, marker=">", markersize=5.5, color=color, clip_on=False, zorder=5)


def style(ax) -> None:
    ax.axvline(1, color="#777777", linestyle=(0, (4, 4)), linewidth=0.8, zorder=0)
    ax.set_xlim(0.08, 4.05)
    ax.set_xticks([0.5, 1, 1.5, 2, 3, 4])
    ax.set_xticklabels(["0.5", "1.0", "1.5", "2.0", "3.0", "4.0"])
    ax.set_xlabel("Relative risk", fontsize=7.5)
    ax.tick_params(axis="both", labelsize=6.5, length=2, width=0.6, pad=2)
    ax.spines[["top", "right"]].set_visible(False)


def plot(a: pd.DataFrame, b: pd.DataFrame, output: Path) -> None:
    plt.rcParams.update({"font.family": "Arial", "font.size": 7, "pdf.fonttype": 42})
    fig, (ax_a, ax_b) = plt.subplots(1, 2, figsize=(510 / 72, 345 / 72),
                                     gridspec_kw={"width_ratios": [1.63, 1]})
    fig.subplots_adjust(left=0.160, right=0.985, top=0.930, bottom=0.205, wspace=0.43)
    rows_a = [
        ("Combined Category 4\n(n = 6 cities)", "Combined all sites (n=6)"),
        ("Pooled mortality\n(n = 3 cities)", "Pooled - Mortality (n=3)"),
        *[(x, x) for x in ["SITE_01", "SITE_04", "SITE_02"]],
        ("Pooled hospitalisation\n(n = 3 cities)", "Pooled - Hospitalisation (n=3)"),
        *[(x, x) for x in ["SITE_03", "SITE_06", "SITE_05"]],
    ]
    y_a = np.arange(len(rows_a) - 1, -1, -1, dtype=float)
    for (_, source), base_y in zip(rows_a, y_a):
        part = a[a.Row_label.eq(source)]
        if len(part) not in (1, 3):
            raise ValueError(f"Unexpected Figure 8a records for {source}")
        for row in part.itertuples(index=False):
            pooled = row.Point_type in ("Pooled", "Combined")
            marker = "D" if pooled else "o"
            size = 6.5 if row.Point_type == "Combined" else (5 if pooled else 4.4)
            offset = 0 if row.Point_type == "Combined" else OFFSETS[row.Category]
            draw(ax_a, row, base_y + offset, marker, size)
    ax_a.set_yticks(y_a, [x[0] for x in rows_a])
    ax_a.set_ylim(-0.8, 8.8)
    ax_a.axhline(6.5, color="#B3B3B3", linestyle=(0, (1, 4)), linewidth=0.7)
    ax_a.axhline(2.5, color="#B3B3B3", linestyle=(0, (1, 4)), linewidth=0.7)
    style(ax_a)

    order_b = ["Age 0-69", "Age >=70", "Female", "Male", "ICD-I Circulatory", "ICD-J Respiratory"]
    display_b = ["Age 0–69", "Age ≥70", "Female", "Male", "ICD-I Circulatory", "ICD-J Respiratory"]
    y_b = np.arange(len(order_b) - 1, -1, -1, dtype=float)
    for source, base_y in zip(order_b, y_b):
        row = b[b.Row_label.eq(source)].iloc[0]
        draw(ax_b, row, base_y, "D", 5)
    ax_b.set_yticks(y_b, display_b)
    ax_b.set_ylim(-0.8, 5.8)
    style(ax_b)

    handles = [Line2D([0], [0], marker="o", linestyle="none", color=COLORS[c],
                      markersize=4.5, label=c) for c in COLORS]
    handles += [
        Line2D([0], [0], marker="o", linestyle="none", color="#4D4D4D", markersize=4.5,
               label="City-specific estimate"),
        Line2D([0], [0], marker="D", linestyle="none", color="#4D4D4D", markersize=4.8,
               label="Pooled estimate"),
    ]
    fig.legend(handles=handles, ncol=5, frameon=False, loc="lower center",
               bbox_to_anchor=(0.5, 0.022), columnspacing=1.05, handletextpad=0.4)
    fig.text(0.012, 0.972, "a", ha="left", va="top", fontsize=9, fontweight="bold")
    fig.text(0.615, 0.972, "b", ha="left", va="top", fontsize=9, fontweight="bold")
    output.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(output, format="pdf", facecolor="white", metadata={"Title": "Figure 8"})
    plt.close(fig)


def main() -> None:
    args = arguments()
    plot(*read_sheets(args.source_data), args.output)
    print(args.output)


if __name__ == "__main__":
    main()
