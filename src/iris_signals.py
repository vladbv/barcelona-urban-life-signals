"""Shared descriptive summaries for the inspected, closure-selected IRIS export."""

from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd

YEAR = 2025
START = pd.Timestamp("2025-01-01")
END = pd.Timestamp("2025-12-31")
MISSING = "(missing)"
OTHER = "Other / missing"
WEEKDAYS = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
COHORT_NOTE = (
    "The headline cohort contains records registered in 2025 and closed in 2025, "
    "as observed in this local export. Requests still open or closed in another year "
    "are absent. Late-year volumes and closure lags are therefore selected by the "
    "year-end cutoff; this is not a complete count of 2025 demand."
)


def validate_prepared(frame: pd.DataFrame) -> None:
    """Reject violations of the observed data contract before producing claims."""
    required = {
        "fitxa_id", "registration_date", "closure_date", "closure_lag_days",
        "area", "district", "support", "request_type",
    }
    missing = required.difference(frame.columns)
    if missing:
        raise ValueError(f"Missing prepared columns: {', '.join(sorted(missing))}")
    if frame.empty:
        raise ValueError("The prepared dataset is empty.")
    if frame["fitxa_id"].isna().any() or frame["fitxa_id"].duplicated().any():
        raise ValueError("Expected one non-missing fitxa_id per prepared record.")
    for column in ["registration_date", "closure_date"]:
        if frame[column].isna().any():
            raise ValueError(f"Missing or invalid {column} values.")
    expected_lag = (frame["closure_date"] - frame["registration_date"]).dt.days
    if expected_lag.lt(0).any() or not expected_lag.eq(frame["closure_lag_days"]).all():
        raise ValueError("Closure lags must be non-negative and match the dates.")
    if not frame["closure_date"].dt.year.eq(YEAR).all():
        raise ValueError("This analysis expects the inspected 2025 closure-year export.")
    if not frame["registration_date"].between(START, END).any():
        raise ValueError("The export has no 2025 registrations to analyse.")


def read_prepared(path: Path) -> pd.DataFrame:
    if not path.is_file():
        raise ValueError(f"File not found: {path}. Run src.prepare_iris_dataset first.")
    frame = pd.read_csv(path, low_memory=False)
    for column in ["registration_date", "closure_date"]:
        if column not in frame:
            raise ValueError(f"Missing prepared column: {column}")
        frame[column] = pd.to_datetime(frame[column], format="%Y-%m-%d", errors="coerce")
    validate_prepared(frame)
    return frame


def registration_cohort(frame: pd.DataFrame) -> pd.DataFrame:
    return frame.loc[frame["registration_date"].between(START, END)].copy()


def daily_metrics(
    frame: pd.DataFrame, start: pd.Timestamp = START, end: pd.Timestamp = END,
) -> pd.DataFrame:
    """Include every calendar day; absent rows mean zero observed export records."""
    calendar = pd.date_range(start, end, freq="D", name="registration_date")
    daily = frame.groupby("registration_date").agg(
        requests=("fitxa_id", "size"),
        median_closure_lag_days=("closure_lag_days", "median"),
        missing_district_percent=("district", lambda values: values.isna().mean() * 100),
    ).reindex(calendar)
    daily["requests"] = daily["requests"].fillna(0).astype(int)
    # Require seven calendar days; do not label a partial window a seven-day average.
    daily["rolling_7_day"] = daily["requests"].rolling(7, min_periods=7).mean()
    daily["weekday"] = daily.index.day_name()
    daily["month"] = daily.index.to_period("M").astype(str)
    return daily.reset_index()


def weekday_summary(daily: pd.DataFrame) -> pd.DataFrame:
    return daily.groupby("weekday").agg(
        calendar_days=("requests", "size"),
        requests=("requests", "sum"),
        mean_daily_requests=("requests", "mean"),
    ).reindex(WEEKDAYS).rename_axis("weekday").reset_index()


def category_summary(frame: pd.DataFrame, column: str) -> pd.DataFrame:
    # Preserve missingness before filling a grouping label, especially district.
    labelled = frame.assign(_district_missing=frame["district"].isna())
    labelled[column] = labelled[column].fillna(MISSING)
    groups = labelled.groupby(column)
    result = groups.agg(
        requests=("fitxa_id", "size"),
        median_closure_lag_days=("closure_lag_days", "median"),
        missing_district_rows=("_district_missing", "sum"),
    ).sort_values("requests", ascending=False)
    result["share_percent"] = result["requests"] / len(frame) * 100
    result["missing_district_percent"] = result["missing_district_rows"] / result["requests"] * 100
    return result.reset_index()


def composition_counts(
    frame: pd.DataFrame, row: str, column: str, top_rows: int = 10, top_columns: int = 8,
) -> pd.DataFrame:
    """Keep the full denominator for each displayed group via an explicit remainder."""
    if frame.empty:
        return pd.DataFrame().rename_axis(row)
    frame = frame.copy()
    frame[row] = frame[row].fillna(MISSING)
    rows = frame[row].value_counts().head(top_rows).index
    columns = frame[column].dropna().value_counts().head(top_columns).index
    frame[column] = frame[column].where(frame[column].isin(columns), OTHER)
    counts = pd.crosstab(frame[row], frame[column]).reindex(
        index=rows, columns=[*columns, OTHER], fill_value=0,
    )
    return counts


def composition_shares(counts: pd.DataFrame) -> pd.DataFrame:
    return counts.div(counts.sum(axis=1).replace(0, np.nan), axis=0) * 100


def closure_histogram(frame: pd.DataFrame) -> pd.DataFrame:
    """Use a separate overflow bucket so long lags are never disguised as 60 days."""
    buckets = pd.cut(
        frame["closure_lag_days"], bins=[-1, 0, 3, 7, 14, 30, 60, float("inf")],
        labels=["0", "1–3", "4–7", "8–14", "15–30", "31–60", ">60"],
    )
    return buckets.value_counts(sort=False).rename_axis("lag_days").reset_index(name="requests")


def volume_lag_correlation(daily: pd.DataFrame) -> float | None:
    """Use all observed days with defined lags, with no arbitrary volume cutoff."""
    pairs = daily[["requests", "median_closure_lag_days"]].dropna()
    if len(pairs) < 3 or pairs.nunique().min() < 2:
        return None
    return float(pairs["requests"].corr(pairs["median_closure_lag_days"]))


def build_tables(frame: pd.DataFrame) -> dict[str, pd.DataFrame]:
    cohort = registration_cohort(frame)
    daily = daily_metrics(cohort)
    monthly = daily.groupby("month").agg(
        requests=("requests", "sum"), calendar_days=("requests", "size"),
        mean_daily_requests=("requests", "mean"),
    )
    months = cohort["registration_date"].dt.to_period("M").astype(str)
    monthly["median_closure_lag_days"] = cohort.groupby(months)["closure_lag_days"].median()
    monthly["p95_closure_lag_days"] = cohort.groupby(months)["closure_lag_days"].quantile(.95)
    # Explicitly show that closure dates count a different cohort (including carry-ins).
    monthly["closures_all_export"] = frame.groupby(
        frame["closure_date"].dt.to_period("M").astype(str)
    ).size().reindex(monthly.index, fill_value=0)
    monthly["max_observable_lag_at_month_start"] = [
        (END - pd.Timestamp(month)).days for month in monthly.index
    ]
    monthly["max_observable_lag_at_month_end"] = [
        (END - pd.Period(month).end_time.normalize()).days for month in monthly.index
    ]
    district_counts = composition_counts(cohort.dropna(subset=["district"]), "district", "area")
    channel_counts = composition_counts(cohort, "area", "support", top_rows=8, top_columns=5)
    return {
        "daily": daily,
        "weekday": weekday_summary(daily),
        "monthly": monthly.reset_index(),
        "areas": category_summary(cohort, "area"),
        "districts": category_summary(cohort, "district"),
        "channels": category_summary(cohort, "support"),
        "request_types": category_summary(cohort, "request_type"),
        "request_type_monthly": pd.crosstab(
            months, cohort["request_type"].fillna(MISSING),
        ).reindex(monthly.index, fill_value=0).rename_axis("month").reset_index(),
        "closure_lag": closure_histogram(cohort),
        "district_area_counts": district_counts.reset_index(),
        "district_area_shares": composition_shares(district_counts).reset_index(),
        "area_channel_counts": channel_counts.reset_index(),
        "area_channel_shares": composition_shares(channel_counts).reset_index(),
    }
