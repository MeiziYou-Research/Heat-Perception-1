#!/usr/bin/env python3
"""Construct frozen seasonal index classifications and HPPI estimates."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np
import pandas as pd

HPII_BREAKS = np.array([
    0.00114114902598386, 0.00178543238369676, 0.00216027065870402,
    0.00238241283234082, 0.00280137357672149, 0.00884031425500674,
])
HPII_Z = np.array([1, 2, 3, 5, 7, 10, 14], dtype=float)
HPVI_Z = np.array([1, 3, 10], dtype=float)
ALPHA = 1.6
SEASONS = ["Spring", "Summer", "Fall", "Winter"]


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--seasonal-input", required=True, type=Path)
    p.add_argument("--annual-reference", type=Path)
    p.add_argument("--output-dir", required=True, type=Path)
    p.add_argument("--expect-cities", type=int, default=347)
    p.add_argument("--expect-continents", type=int, default=6)
    return p.parse_args()


def hppi(shares: np.ndarray, z: np.ndarray) -> float:
    p = np.asarray(shares, dtype=float)
    if p.sum() <= 0:
        return float("nan")
    p = p / p.sum()
    mu = float(np.dot(p, z))
    if mu <= 0:
        return 0.0
    distances = np.abs(z[:, None] - z[None, :])
    weights = (p ** (1.0 + ALPHA))[:, None] * p[None, :]
    return float(np.sum(weights * distances) / (2.0 * mu))


def validate_input(df: pd.DataFrame, expected: int, expected_continents: int) -> None:
    required = {"city_id", "continent", "season", "HPII", "HPVI"}
    missing = sorted(required - set(df.columns))
    if missing:
        raise ValueError(f"Missing columns: {missing}")
    if df.duplicated(["city_id", "season"]).any():
        raise ValueError("Duplicate city_id-season records")
    if set(df["season"].dropna()) != set(SEASONS):
        raise ValueError("Season labels must be Spring, Summer, Fall, and Winter")
    counts = df.groupby("season")["city_id"].nunique()
    if not (counts == expected).all():
        raise ValueError(f"Expected {expected} cities in every season; found {counts.to_dict()}")
    city_sets = {
        season: set(group["city_id"])
        for season, group in df.groupby("season", observed=True)
    }
    reference_set = city_sets[SEASONS[0]]
    inconsistent = [season for season in SEASONS if city_sets[season] != reference_set]
    if inconsistent:
        raise ValueError(
            "Every season must contain the same city_id set; mismatches found for "
            + ", ".join(inconsistent)
        )
    if df["city_id"].isna().any() or df["continent"].isna().any():
        raise ValueError("city_id and continent must not contain missing values")
    continent_per_city = df.groupby("city_id")["continent"].nunique(dropna=False)
    if (continent_per_city != 1).any():
        raise ValueError("Each city_id must have one consistent continent across seasons")
    if df["continent"].nunique() != expected_continents:
        raise ValueError(
            f"Expected {expected_continents} continents; found {df['continent'].nunique()}"
        )
    values = df[["HPII", "HPVI"]].apply(pd.to_numeric, errors="coerce")
    if not np.isfinite(values.to_numpy()).all():
        raise ValueError("HPII and HPVI must contain finite numeric values")
    if not values["HPII"].between(0, 1, inclusive="both").all():
        raise ValueError("HPII must lie between 0 and 1")
    if (values["HPVI"] < 0).any():
        raise ValueError("HPVI must be non-negative")


def classify(df: pd.DataFrame) -> pd.DataFrame:
    out = df.copy()
    out["HPII_level"] = np.searchsorted(HPII_BREAKS, out["HPII"].to_numpy(float), side="left") + 1
    out["HPVI_category"] = pd.cut(
        out["HPVI"].astype(float), [-np.inf, 0.15, 0.30, np.inf],
        labels=["Low", "Moderate", "High"], right=True,
    ).astype(str)
    return out


def summarize(df: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    estimates, shares = [], []
    for (continent, season), sub in df.groupby(["continent", "season"], sort=True):
        for metric, categories, z in (
            ("HPPI(I)", list(range(1, 8)), HPII_Z),
            ("HPPI(V)", ["Low", "Moderate", "High"], HPVI_Z),
        ):
            source = sub["HPII_level"] if metric == "HPPI(I)" else sub["HPVI_category"]
            counts = np.array([(source == category).sum() for category in categories], dtype=int)
            proportions = counts / counts.sum()
            estimates.append({
                "continent": continent, "season": season, "n_cities": int(counts.sum()),
                "metric": metric, "HPPI": hppi(proportions, z), "alpha": ALPHA,
                "normalization": "k=1/(2*mu)",
            })
            for category, count, proportion, representative in zip(categories, counts, proportions, z):
                shares.append({
                    "continent": continent, "season": season, "metric": metric,
                    "category": category, "count": int(count), "total": int(counts.sum()),
                    "proportion": float(proportion), "representative_value": float(representative),
                })
    return pd.DataFrame(estimates), pd.DataFrame(shares)


def main() -> None:
    args = parse_args()
    df = pd.read_csv(args.seasonal_input)
    validate_input(df, args.expect_cities, args.expect_continents)
    classified = classify(df)
    estimates, shares = summarize(classified)
    expected_estimates = classified["continent"].nunique() * 4 * 2
    if len(estimates) != expected_estimates:
        raise ValueError(f"Expected {expected_estimates} HPPI estimates; found {len(estimates)}")
    if args.annual_reference:
        annual = pd.read_csv(args.annual_reference)
        if not {"city_id", "annual_HPII"}.issubset(annual.columns):
            raise ValueError("Annual reference requires city_id and annual_HPII")
        if annual["city_id"].isna().any() or annual["city_id"].duplicated().any():
            raise ValueError("Annual reference city_id values must be complete and unique")
        if set(annual["city_id"]) != set(classified["city_id"]):
            raise ValueError("Annual reference city_id set must exactly match the seasonal input")
        annual_hpii = pd.to_numeric(annual["annual_HPII"], errors="coerce")
        if not np.isfinite(annual_hpii.to_numpy()).all() or not annual_hpii.between(0, 1).all():
            raise ValueError("annual_HPII must contain finite values between 0 and 1")
    args.output_dir.mkdir(parents=True, exist_ok=True)
    classified.to_csv(args.output_dir / "city_season_indices.csv", index=False)
    estimates.to_csv(args.output_dir / "continent_season_hppi.csv", index=False)
    shares.to_csv(args.output_dir / "continent_season_group_shares.csv", index=False)
    metadata = {
        "expected_cities": args.expect_cities, "expected_continents": args.expect_continents,
        "alpha": ALPHA,
        "normalization": "k=1/(2*mu)", "HPII_breaks": HPII_BREAKS.tolist(),
        "HPVI_thresholds": [0.15, 0.30], "HPII_representative_values": HPII_Z.tolist(),
        "HPVI_representative_values": HPVI_Z.tolist(),
    }
    (args.output_dir / "analysis_specification.json").write_text(json.dumps(metadata, indent=2), encoding="utf-8")
    print(f"Validated {args.expect_cities} cities per season; wrote {len(estimates)} HPPI estimates.")


if __name__ == "__main__":
    main()
