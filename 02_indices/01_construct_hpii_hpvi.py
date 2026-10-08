#!/usr/bin/env python3
"""Construct city-season HPII and HPVI from city-day counts.

Primary HPII is the untransformed seasonal ratio of heat-perception posts
to all eligible posts. City-month median de-centering and 1st/99th
percentile winsorisation are exported as explicit preprocessing variables;
they do not replace the primary HPII ratio.

HPVI is calculated as the seasonal mean of valid trailing seven-day
coefficients of variation in the completed daily heat-perception-post count
series within each city-season.
"""

from __future__ import annotations

import argparse
from pathlib import Path

import numpy as np
import pandas as pd


SEASON_ORDER = ["Spring", "Summer", "Fall", "Winter"]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--daily-input", required=True, type=Path)
    parser.add_argument("--output-dir", required=True, type=Path)
    parser.add_argument("--city-col", default="city_id")
    parser.add_argument("--date-col", default="date")
    parser.add_argument("--heat-posts-col", default="heat_posts")
    parser.add_argument("--total-posts-col", default="total_posts")
    parser.add_argument("--hemisphere-col", default="hemisphere")
    parser.add_argument("--continent-col", default="continent")
    parser.add_argument("--event-flag-col", default=None)
    parser.add_argument("--winsor-lower", type=float, default=0.01)
    parser.add_argument("--winsor-upper", type=float, default=0.99)
    parser.add_argument("--rolling-days", type=int, default=7)
    return parser.parse_args()


def season_from_month(month: int, hemisphere: str) -> str:
    north = str(hemisphere).strip().lower().startswith("n")
    if north:
        mapping = {
            12: "Winter", 1: "Winter", 2: "Winter",
            3: "Spring", 4: "Spring", 5: "Spring",
            6: "Summer", 7: "Summer", 8: "Summer",
            9: "Fall", 10: "Fall", 11: "Fall",
        }
    else:
        mapping = {
            12: "Summer", 1: "Summer", 2: "Summer",
            3: "Fall", 4: "Fall", 5: "Fall",
            6: "Winter", 7: "Winter", 8: "Winter",
            9: "Spring", 10: "Spring", 11: "Spring",
        }
    return mapping[int(month)]


def validate_input(df: pd.DataFrame, args: argparse.Namespace) -> pd.DataFrame:
    required = {
        args.city_col, args.date_col, args.heat_posts_col,
        args.total_posts_col, args.hemisphere_col, args.continent_col,
    }
    missing = sorted(required.difference(df.columns))
    if missing:
        raise ValueError(f"Missing required columns: {missing}")
    if args.event_flag_col and args.event_flag_col not in df.columns:
        raise ValueError(f"Missing event flag column: {args.event_flag_col}")
    out = df.copy()
    out[args.date_col] = pd.to_datetime(out[args.date_col], errors="coerce")
    if out[args.date_col].isna().any():
        raise ValueError("The date column contains unparseable values")
    if out.duplicated([args.city_col, args.date_col]).any():
        raise ValueError("Input must contain at most one row per city and date")
    for col in [args.heat_posts_col, args.total_posts_col]:
        out[col] = pd.to_numeric(out[col], errors="coerce")
        if out[col].isna().any() or (out[col] < 0).any():
            raise ValueError(f"{col} must contain non-negative numeric values")
    if (out[args.heat_posts_col] > out[args.total_posts_col]).any():
        raise ValueError("heat_posts cannot exceed total_posts")
    if not 0 <= args.winsor_lower < args.winsor_upper <= 1:
        raise ValueError("Winsor quantiles must satisfy 0 <= lower < upper <= 1")
    if args.rolling_days < 2:
        raise ValueError("rolling-days must be at least 2")
    return out.sort_values([args.city_col, args.date_col]).reset_index(drop=True)


def add_hpii_normalisation(df: pd.DataFrame, args: argparse.Namespace) -> pd.DataFrame:
    out = df.copy()
    out["month"] = out[args.date_col].dt.to_period("M").astype(str)
    out["daily_HPII_raw"] = np.where(
        out[args.total_posts_col] > 0,
        out[args.heat_posts_col] / out[args.total_posts_col],
        np.nan,
    )
    if args.event_flag_col and args.event_flag_col in out.columns:
        event = pd.to_numeric(out[args.event_flag_col], errors="coerce").fillna(0)
        out["baseline_eligible"] = event.eq(0)
    else:
        out["baseline_eligible"] = True

    keys = [out[args.city_col], out["month"]]
    eligible_values = out["daily_HPII_raw"].where(out["baseline_eligible"])
    eligible_median = eligible_values.groupby(keys, observed=True).transform("median")
    fallback_median = out["daily_HPII_raw"].groupby(keys, observed=True).transform("median")
    out["city_month_HPII_median"] = eligible_median.fillna(fallback_median)
    out["daily_HPII_decentered"] = (
        out["daily_HPII_raw"] - out["city_month_HPII_median"]
    )
    grouped_residual = out["daily_HPII_decentered"].groupby(keys, observed=True)
    out["winsor_lower_bound"] = grouped_residual.transform(
        lambda values: values.quantile(args.winsor_lower)
    )
    out["winsor_upper_bound"] = grouped_residual.transform(
        lambda values: values.quantile(args.winsor_upper)
    )
    out["daily_HPII_decentered_winsorised"] = np.minimum(
        np.maximum(
            out["daily_HPII_decentered"], out["winsor_lower_bound"]
        ),
        out["winsor_upper_bound"],
    )
    return out.sort_values([args.city_col, args.date_col]).reset_index(drop=True)


def complete_daily_hpvi_series(df: pd.DataFrame, args: argparse.Namespace) -> pd.DataFrame:
    rows = []
    for city_id, group in df.groupby(args.city_col, sort=False):
        group = group.sort_values(args.date_col).copy()
        hemispheres = group[args.hemisphere_col].dropna().astype(str).unique()
        continents = group[args.continent_col].dropna().astype(str).unique()
        if len(hemispheres) != 1 or len(continents) != 1:
            raise ValueError(f"City {city_id!r} has inconsistent geographic metadata")
        calendar = pd.DataFrame(
            {args.date_col: pd.date_range(group[args.date_col].min(), group[args.date_col].max())}
        )
        completed = calendar.merge(group, on=args.date_col, how="left")
        completed[args.city_col] = city_id
        completed[args.hemisphere_col] = hemispheres[0]
        completed[args.continent_col] = continents[0]
        completed["date_observed"] = completed[args.heat_posts_col].notna()
        completed["heat_posts_filled_for_HPVI"] = completed[args.heat_posts_col].fillna(
            float(group[args.heat_posts_col].median())
        )
        completed["season"] = completed[args.date_col].dt.month.map(
            lambda month: season_from_month(month, hemispheres[0])
        )
        rows.append(completed)
    return pd.concat(rows, ignore_index=True)


def calculate_hpvi(completed: pd.DataFrame, args: argparse.Namespace):
    data = completed.sort_values([args.city_col, "season", args.date_col]).copy()
    grouped = data.groupby(
        [args.city_col, "season"], observed=True
    )["heat_posts_filled_for_HPVI"]
    data["rolling_mean_7d"] = grouped.transform(
        lambda series: series.rolling(args.rolling_days, min_periods=1).mean()
    )
    data["rolling_sd_7d"] = grouped.transform(
        lambda series: series.rolling(args.rolling_days, min_periods=2).std(ddof=1)
    )
    data["rolling_cv_7d"] = np.where(
        data["rolling_mean_7d"] > 0,
        data["rolling_sd_7d"] / data["rolling_mean_7d"],
        np.nan,
    )
    hpvi = (
        data.groupby([args.city_col, "season"], observed=True)
        .agg(
            HPVI=("rolling_cv_7d", "mean"),
            HPVI_windows=("rolling_cv_7d", "count"),
        )
        .reset_index()
    )
    return data, hpvi


def calculate_seasonal_hpii(df: pd.DataFrame, args: argparse.Namespace) -> pd.DataFrame:
    data = df.copy()
    data["season"] = [
        season_from_month(month, hemisphere)
        for month, hemisphere in zip(
            data[args.date_col].dt.month, data[args.hemisphere_col]
        )
    ]
    seasonal = (
        data.groupby(
            [args.city_col, args.continent_col, "season"], observed=True
        )
        .agg(
            heat_posts=(args.heat_posts_col, "sum"),
            total_posts=(args.total_posts_col, "sum"),
            observed_days=(args.date_col, "nunique"),
        )
        .reset_index()
    )
    seasonal["HPII"] = np.where(
        seasonal["total_posts"] > 0,
        seasonal["heat_posts"] / seasonal["total_posts"],
        np.nan,
    )
    return seasonal


def main() -> None:
    args = parse_args()
    daily = validate_input(pd.read_csv(args.daily_input, low_memory=False), args)
    normalized = add_hpii_normalisation(daily, args)
    completed = complete_daily_hpvi_series(daily, args)
    hpvi_daily, hpvi = calculate_hpvi(completed, args)
    seasonal = calculate_seasonal_hpii(daily, args).merge(
        hpvi, on=[args.city_col, "season"], how="left", validate="one_to_one"
    )
    seasonal["season"] = pd.Categorical(
        seasonal["season"], SEASON_ORDER, ordered=True
    )
    seasonal = seasonal.sort_values([args.city_col, "season"]).reset_index(drop=True)
    args.output_dir.mkdir(parents=True, exist_ok=True)
    normalized.to_csv(args.output_dir / "city_day_hpii_preprocessing.csv", index=False)
    hpvi_daily.to_csv(args.output_dir / "city_day_hpvi_rolling.csv", index=False)
    seasonal.to_csv(args.output_dir / "city_season_hpii_hpvi.csv", index=False)


if __name__ == "__main__":
    main()
