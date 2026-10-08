#!/usr/bin/env python3
"""Standardise labelled inputs without inventing geographic metadata.

The public demonstration uses ``text``, ``example_id`` and optional synthetic
``group_id``. Production data may use different column names; pass them via the
command-line options. This script never creates city, country or continent
fields and never claims to reconstruct the manuscript split.
"""

from __future__ import annotations
import argparse
import json
from pathlib import Path
import pandas as pd


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input_csv", required=True)
    parser.add_argument("--output_csv", required=True)
    parser.add_argument("--text_col", default="text")
    parser.add_argument("--label_col", default="label")
    parser.add_argument("--id_col", default="example_id")
    parser.add_argument("--group_col", default="group_id")
    parser.add_argument("--month_col", default="month")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    frame = pd.read_csv(args.input_csv)
    required = [args.text_col, args.label_col]
    missing = [column for column in required if column not in frame.columns]
    if missing:
        raise ValueError(f"Missing required columns: {missing}")

    out = pd.DataFrame({
        "example_id": frame[args.id_col].astype(str) if args.id_col in frame else [f"EX_{i:06d}" for i in range(1, len(frame) + 1)],
        "text": frame[args.text_col].astype(str),
        "label": frame[args.label_col].astype(int),
    })
    for source, target in [
        (args.month_col, "month"), ("example_category", "example_category"),
        (args.group_col, "group_id"), ("is_synthetic", "is_synthetic"),
    ]:
        if source in frame.columns:
            out[target] = frame[source]

    if "month" in out:
        out["month"] = pd.to_numeric(out["month"], errors="raise").astype(int)
        if not out["month"].between(1, 12).all():
            raise ValueError("month must be encoded as integers 1-12")
    if "is_synthetic" not in out:
        out["is_synthetic"] = False

    Path(args.output_csv).parent.mkdir(parents=True, exist_ok=True)
    out.to_csv(args.output_csv, index=False)
    print(json.dumps({"rows": len(out), "columns": out.columns.tolist()}, indent=2))


if __name__ == "__main__":
    main()
