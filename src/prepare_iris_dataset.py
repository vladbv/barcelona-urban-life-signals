"""Prepare a conservative analysis-ready IRIS dataset from the raw CSV."""

from __future__ import annotations

import argparse
from pathlib import Path

import pandas as pd

from src.profile_iris import add_observed_dates, markdown_table, read_csv


DEFAULT_OUTPUT_PATH = Path("data/processed/iris_2025_clean.csv")
DEFAULT_REPORT_PATH = Path("reports/iris_prepare_summary.md")

COLUMN_MAP = {
    "FITXA_ID": "fitxa_id",
    "TIPUS": "request_type",
    "AREA": "area",
    "ELEMENT": "element",
    "DETALL": "detail",
    "CODI_DISTRICTE": "district_code",
    "DISTRICTE": "district",
    "CODI_BARRI": "neighborhood_code",
    "BARRI": "neighborhood",
    "SECCIO_CENSAL": "census_section",
    "LONGITUD": "longitude",
    "LATITUD": "latitude",
    "SUPORT": "support",
    "CANALS_RESPOSTA": "response_channels",
}
OUTPUT_COLUMNS = [
    "fitxa_id",
    "request_type",
    "area",
    "element",
    "detail",
    "registration_date",
    "closure_date",
    "closure_lag_days",
    "district_code",
    "district",
    "neighborhood_code",
    "neighborhood",
    "census_section",
    "longitude",
    "latitude",
    "support",
    "response_channels",
]
INTEGER_COLUMNS = [
    "fitxa_id",
    "district_code",
    "neighborhood_code",
    "census_section",
    "closure_lag_days",
]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Create a conservative processed IRIS CSV with exact duplicates "
            "removed, parsed dates, and observed columns renamed."
        )
    )
    parser.add_argument("csv_path", type=Path, help="path to the raw IRIS CSV")
    parser.add_argument(
        "--output-path",
        type=Path,
        default=DEFAULT_OUTPUT_PATH,
        help=f"processed CSV path (default: {DEFAULT_OUTPUT_PATH})",
    )
    parser.add_argument(
        "--report-path",
        type=Path,
        default=DEFAULT_REPORT_PATH,
        help=f"Markdown summary path (default: {DEFAULT_REPORT_PATH})",
    )
    return parser.parse_args()


def prepare_dataset(raw_frame: pd.DataFrame) -> pd.DataFrame:
    deduplicated = raw_frame.drop_duplicates().copy()
    frame = add_observed_dates(deduplicated)
    frame["closure_lag_days"] = (
        frame["closure_date"] - frame["registration_date"]
    ).dt.days

    missing_source_columns = [
        column for column in COLUMN_MAP if column not in frame.columns
    ]
    if missing_source_columns:
        raise ValueError(
            "Missing expected observed columns: "
            + ", ".join(sorted(missing_source_columns))
        )

    prepared = frame.rename(columns=COLUMN_MAP)
    for column in INTEGER_COLUMNS:
        prepared[column] = pd.to_numeric(prepared[column], errors="coerce").astype(
            "Int64"
        )
    return prepared[OUTPUT_COLUMNS].sort_values(
        ["registration_date", "fitxa_id"], kind="stable"
    )


def build_summary(raw_frame: pd.DataFrame, prepared: pd.DataFrame, output_path: Path) -> str:
    duplicate_rows_removed = len(raw_frame) - len(raw_frame.drop_duplicates())
    repeated_ids_after_cleaning = int(prepared["fitxa_id"].duplicated().sum())
    date_summary = pd.DataFrame(
        [
            {
                "field": "registration_date",
                "min": prepared["registration_date"].min().date(),
                "max": prepared["registration_date"].max().date(),
                "missing": int(prepared["registration_date"].isna().sum()),
            },
            {
                "field": "closure_date",
                "min": prepared["closure_date"].min().date(),
                "max": prepared["closure_date"].max().date(),
                "missing": int(prepared["closure_date"].isna().sum()),
            },
        ]
    )
    row_summary = pd.DataFrame(
        [
            {"metric": "raw rows", "value": len(raw_frame)},
            {"metric": "exact duplicate rows removed", "value": duplicate_rows_removed},
            {"metric": "processed rows", "value": len(prepared)},
            {
                "metric": "repeated fitxa_id after cleaning",
                "value": repeated_ids_after_cleaning,
            },
            {
                "metric": "negative closure lag rows",
                "value": int((prepared["closure_lag_days"] < 0).sum()),
            },
        ]
    )
    missing_summary = pd.DataFrame(
        {
            "column": prepared.columns,
            "missing_rows": [int(prepared[column].isna().sum()) for column in prepared],
            "missing_percent": [
                round(float(prepared[column].isna().mean() * 100), 2)
                for column in prepared
            ],
        }
    )

    return "\n\n".join(
        [
            "# IRIS preparation summary",
            f"Processed output: `{output_path}`",
            "## Row checks",
            markdown_table(row_summary),
            "## Date checks",
            markdown_table(date_summary),
            "## Missingness after preparation",
            markdown_table(missing_summary),
            "## Rules applied",
            "- Removed exact duplicate rows only.",
            "- Parsed registration and closure dates from the observed day/month/year columns.",
            "- Kept both registration and closure dates with explicit names.",
            "- Added `closure_lag_days` for later resolution-time checks.",
            "- Renamed selected observed columns to stable snake_case names.",
            "## Rules not applied",
            "- No imputation.",
            "- No category merging.",
            "- No removal of records with missing geography.",
            "- No modelling features.",
        ]
    )


def main() -> int:
    args = parse_args()
    raw_frame = read_csv(args.csv_path)
    prepared = prepare_dataset(raw_frame)

    args.output_path.parent.mkdir(parents=True, exist_ok=True)
    prepared.to_csv(args.output_path, index=False)

    report = build_summary(raw_frame, prepared, args.output_path)
    args.report_path.parent.mkdir(parents=True, exist_ok=True)
    args.report_path.write_text(report + "\n", encoding="utf-8")

    print(f"Wrote processed dataset: {args.output_path}")
    print(f"Wrote preparation summary: {args.report_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
