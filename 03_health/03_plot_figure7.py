#!/usr/bin/env python3
"""Render main-text Figure 7 from the Nature Communications Source Data."""

from __future__ import annotations

import argparse
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

ORDER = ["P-P", "P-S", "P-T", "S-P", "S-S", "S-T", "T-P", "T-S", "T-T"]
OUTCOMES = ["Mortality", "Hospitalisation", "ED visits"]
COLORS = {
    "P-P": "#0B3C78", "P-S": "#4F91C6", "P-T": "#C6DBEF",
    "S-P": "#B7D3EA", "S-S": "#BDBDBD", "S-T": "#F3C89D",
    "T-P": "#FED976", "T-S": "#E66101", "T-T": "#B2182B",
}


def arguments() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source-data", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    return parser.parse_args()


def read_sheet(path: Path) -> pd.DataFrame:
    data = pd.read_excel(path, sheet_name="Fig. 7", header=0)
    required = {"Outcome", "Performance_class", "Count", "Total_city_outcome_pairs", "Proportion"}
    missing = required - set(data.columns)
    if missing:
        raise ValueError(f"Figure 7 sheet is missing columns: {sorted(missing)}")
    data = data[list(required)].copy()
    if set(data["Outcome"]) != set(OUTCOMES):
        raise ValueError("Unexpected Figure 7 outcome labels")
    if not set(data["Performance_class"]).issubset(ORDER):
        raise ValueError("Unexpected Figure 7 model-comparison class")
    for outcome, group in data.groupby("Outcome"):
        if len(group) != len(ORDER) or set(group["Performance_class"]) != set(ORDER):
            raise ValueError(f"Expected one row for each of the nine classes for {outcome}")
        numeric = group[["Count", "Total_city_outcome_pairs", "Proportion"]]
        if not np.isfinite(numeric.to_numpy(dtype=float)).all():
            raise ValueError(f"Non-finite counts, totals or proportions for {outcome}")
        if (group["Count"] < 0).any() or not (group["Count"] % 1 == 0).all():
            raise ValueError(f"Counts must be non-negative integers for {outcome}")
        totals = group["Total_city_outcome_pairs"].unique()
        if (len(totals) != 1 or totals[0] <= 0 or totals[0] % 1 != 0
                or group["Count"].sum() != totals[0]):
            raise ValueError(f"Counts do not equal the declared total for {outcome}")
        expected = group["Count"] / group["Total_city_outcome_pairs"]
        if not expected.round(12).equals(group["Proportion"].round(12)):
            raise ValueError(f"Proportions do not match counts for {outcome}")
    return data


def plot(data: pd.DataFrame, output: Path) -> None:
    plt.rcParams.update({"font.family": "Arial", "font.size": 7, "pdf.fonttype": 42,
                         "mathtext.fontset": "custom", "mathtext.rm": "Arial",
                         "mathtext.it": "Arial:italic"})
    fig, ax = plt.subplots(figsize=(492.22113037109375 / 72, 330.6435852050781 / 72))
    bottom = [0.0] * len(OUTCOMES)
    for category in ORDER:
        values = []
        for outcome in OUTCOMES:
            row = data[(data.Outcome == outcome) & (data.Performance_class == category)]
            values.append(float(row.Proportion.iloc[0]) if len(row) else 0.0)
        ax.bar(range(len(OUTCOMES)), values, bottom=bottom, width=0.56,
               color=COLORS[category], edgecolor="none", label=category)
        bottom = [x + y for x, y in zip(bottom, values)]
    totals = data.groupby("Outcome")["Total_city_outcome_pairs"].first()
    ax.set_xticks(range(len(OUTCOMES)), OUTCOMES)
    ax.set_xlim(-0.41, 2.41)
    ax.set_ylim(0, 1.075)
    ax.set_yticks([0, 0.25, 0.5, 0.75, 1], ["0%", "25%", "50%", "75%", "100%"])
    ax.set_ylabel("Proportion of city–outcome pairs")
    for i, outcome in enumerate(OUTCOMES):
        ax.text(i, 1.014, rf"$\mathit{{n}}$ = {int(totals[outcome])}",
                ha="center", va="bottom")
    ax.spines[["top", "right"]].set_visible(False)
    for spine in ("left", "bottom"):
        ax.spines[spine].set_linewidth(0.65)
    ax.tick_params(length=3, width=0.65)
    ax.legend(ncol=9, frameon=False, loc="lower center", bbox_to_anchor=(0.5, 1.063),
              handlelength=1.6, columnspacing=1.3, handletextpad=0.5, fontsize=7)
    fig.subplots_adjust(left=0.078, right=0.995, top=0.90, bottom=0.050)
    output.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(output, format="pdf", facecolor="white", metadata={"Title": "Figure 7"})
    plt.close(fig)


def main() -> None:
    args = arguments()
    plot(read_sheet(args.source_data), args.output)
    print(args.output)


if __name__ == "__main__":
    main()
