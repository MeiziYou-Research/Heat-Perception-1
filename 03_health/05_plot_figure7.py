#!/usr/bin/env python3
"""Render main-text Figure 7 from the Nature Communications Source Data."""

from __future__ import annotations

import argparse
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd

ORDER = ["P-P", "P-S", "S-P", "S-S", "S-T", "T-S", "T-T"]
OUTCOMES = ["Mortality", "Hospitalisation", "ED visits"]
COLORS = {
    "P-P": "#2166AC", "P-S": "#67A9CF", "S-P": "#92C5DE",
    "S-S": "#D9D9D9", "S-T": "#F4A582", "T-S": "#EF8A62",
    "T-T": "#B2182B",
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
        totals = group["Total_city_outcome_pairs"].unique()
        if len(totals) != 1 or int(group["Count"].sum()) != int(totals[0]):
            raise ValueError(f"Counts do not equal the declared total for {outcome}")
        expected = group["Count"] / group["Total_city_outcome_pairs"]
        if not expected.round(12).equals(group["Proportion"].round(12)):
            raise ValueError(f"Proportions do not match counts for {outcome}")
    return data


def plot(data: pd.DataFrame, output: Path) -> None:
    plt.rcParams.update({"font.family": "Arial", "font.size": 7.5, "pdf.fonttype": 42})
    fig, ax = plt.subplots(figsize=(180 / 25.4, 92 / 25.4))
    left = [0.0] * len(OUTCOMES)
    for category in ORDER:
        values = []
        for outcome in OUTCOMES:
            row = data[(data.Outcome == outcome) & (data.Performance_class == category)]
            values.append(float(row.Proportion.iloc[0]) if len(row) else 0.0)
        ax.barh(OUTCOMES, values, left=left, height=0.56, color=COLORS[category],
                edgecolor="white", linewidth=0.5, label=category)
        left = [x + y for x, y in zip(left, values)]
    totals = data.groupby("Outcome")["Total_city_outcome_pairs"].first()
    ax.set_yticks(
        range(len(OUTCOMES)),
        [f"{outcome} (n = {int(totals[outcome])})" for outcome in OUTCOMES],
    )
    ax.set_xlim(0, 1)
    ax.set_xticks([0, 0.25, 0.5, 0.75, 1])
    ax.set_xticklabels(["0", "25", "50", "75", "100"])
    ax.set_xlabel("Proportion of city–outcome comparisons (%)")
    ax.invert_yaxis()
    ax.spines[["top", "right", "left"]].set_visible(False)
    ax.tick_params(axis="y", length=0)
    ax.legend(title="Model-comparison class", ncol=7, frameon=False,
              loc="lower center", bbox_to_anchor=(0.5, -0.34),
              handlelength=1.4, columnspacing=1.0)
    fig.subplots_adjust(left=0.22, right=0.98, top=0.96, bottom=0.29)
    output.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(output, format="pdf", facecolor="white", metadata={"Title": "Figure 7"})
    plt.close(fig)


def main() -> None:
    args = arguments()
    plot(read_sheet(args.source_data), args.output)
    print(args.output)


if __name__ == "__main__":
    main()
