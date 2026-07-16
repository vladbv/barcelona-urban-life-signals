"""Investigate specific data-quality questions in the observed IRIS export."""

from __future__ import annotations

import argparse
from pathlib import Path

import pandas as pd

from src.profile_iris import add_observed_dates, markdown_table, read_csv, top_values


DEFAULT_REPORT_PATH = Path("reports/iris_quality_notes.md")
DISPLAY_COLUMNS = [
    "FITXA_ID",
    "TIPUS",
    "AREA",
    "ELEMENT",
    "DETALL",
    "DISTRICTE",
    "BARRI",
    "SUPORT",
    "registration_date",
    "closure_date",
]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Write a Markdown report for duplicate FITXA_ID rows and "
            "registration-vs-closure timing in an observed IRIS CSV."
        )
    )
    parser.add_argument("csv_path", type=Path, help="path to the raw IRIS CSV")
    parser.add_argument(
        "--report-path",
        type=Path,
        default=DEFAULT_REPORT_PATH,
        help=f"Markdown report path (default: {DEFAULT_REPORT_PATH})",
    )
    return parser.parse_args()


def duplicate_group_summary(frame: pd.DataFrame) -> pd.DataFrame:
    if "FITXA_ID" not in frame.columns:
        return pd.DataFrame(
            [{"metric": "FITXA_ID column present", "value": "no"}]
        )

    duplicate_mask = frame["FITXA_ID"].duplicated(keep=False)
    duplicate_rows = frame.loc[duplicate_mask]
    duplicated_ids = duplicate_rows["FITXA_ID"].nunique()
    max_rows_per_id = (
        duplicate_rows.groupby("FITXA_ID").size().max()
        if not duplicate_rows.empty
        else 0
    )
    remaining_repeated_ids = frame.drop_duplicates()["FITXA_ID"].duplicated().sum()

    return pd.DataFrame(
        [
            {"metric": "rows with duplicated FITXA_ID", "value": len(duplicate_rows)},
            {"metric": "distinct duplicated FITXA_ID values", "value": duplicated_ids},
            {"metric": "max rows for one FITXA_ID", "value": int(max_rows_per_id)},
            {
                "metric": "repeated FITXA_ID values after exact de-duplication",
                "value": int(remaining_repeated_ids),
            },
        ]
    )


def duplicate_examples(frame: pd.DataFrame, limit_ids: int = 5) -> pd.DataFrame:
    if "FITXA_ID" not in frame.columns:
        return pd.DataFrame()

    duplicated_ids = (
        frame.loc[frame["FITXA_ID"].duplicated(keep=False), "FITXA_ID"]
        .drop_duplicates()
        .head(limit_ids)
    )
    columns = [column for column in DISPLAY_COLUMNS if column in frame.columns]
    examples = frame.loc[frame["FITXA_ID"].isin(duplicated_ids), columns].copy()
    for column in ["registration_date", "closure_date"]:
        if column in examples.columns:
            examples[column] = examples[column].dt.date
    return examples


def timing_summary(frame: pd.DataFrame) -> pd.DataFrame:
    lag_days = (frame["closure_date"] - frame["registration_date"]).dt.days
    return pd.DataFrame(
        [
            {"metric": "rows", "value": len(frame)},
            {
                "metric": "registration before closure year",
                "value": int((frame["registration_date"].dt.year < frame["closure_date"].dt.year).sum()),
            },
            {
                "metric": "registration in closure year",
                "value": int((frame["registration_date"].dt.year == frame["closure_date"].dt.year).sum()),
            },
            {
                "metric": "negative closure-registration lag",
                "value": int((lag_days < 0).sum()),
            },
            {"metric": "min lag days", "value": int(lag_days.min())},
            {"metric": "median lag days", "value": int(lag_days.median())},
            {"metric": "95th percentile lag days", "value": int(lag_days.quantile(0.95))},
            {"metric": "max lag days", "value": int(lag_days.max())},
        ]
    )


def registrations_by_year(frame: pd.DataFrame) -> pd.DataFrame:
    counts = (
        frame["registration_date"]
        .dt.year
        .value_counts()
        .sort_index()
        .rename_axis("registration_year")
        .reset_index(name="rows")
    )
    counts["percent"] = (counts["rows"] / len(frame) * 100).round(2)
    return counts


def older_registration_examples(frame: pd.DataFrame, limit: int = 10) -> pd.DataFrame:
    older = frame.loc[
        frame["registration_date"].dt.year < frame["closure_date"].dt.year
    ].copy()
    columns = [column for column in DISPLAY_COLUMNS if column in older.columns]
    examples = older.sort_values(["registration_date", "closure_date"]).head(limit)[
        columns
    ]
    for column in ["registration_date", "closure_date"]:
        if column in examples.columns:
            examples[column] = examples[column].dt.date
    return examples


def build_report(frame: pd.DataFrame, csv_path: Path) -> str:
    duplicate_summary = duplicate_group_summary(frame)
    duplicate_sample = duplicate_examples(frame)
    timing = timing_summary(frame)
    year_counts = registrations_by_year(frame)
    older_examples = older_registration_examples(frame)

    sections = [
        "# IRIS quality notes",
        f"Source file: `{csv_path}`",
        "## Duplicate `FITXA_ID` review",
        markdown_table(duplicate_summary),
        "### Example duplicated rows",
        markdown_table(duplicate_sample),
        "## Registration and closure timing",
        markdown_table(timing),
        "### Registration years inside this export",
        markdown_table(year_counts),
        "### Top request types among records registered before their closure year",
        markdown_table(
            top_values(
                frame.loc[
                    frame["registration_date"].dt.year < frame["closure_date"].dt.year
                ],
                "TIPUS",
            )
        ),
        "### Oldest registration examples in this export",
        markdown_table(older_examples),
        "## Working interpretation",
        (
            "- The 2025 CSV appears to be organised by closure year, not purely "
            "by registration year. That explains why some records were opened "
            "before 2025 but closed during 2025."
        ),
        (
            "- For first analysis, date choice must be explicit: registration "
            "date is better for demand/reporting rhythm; closure date is better "
            "for council resolution timing."
        ),
        (
            "- The duplicate rows currently look safe to remove only as exact "
            "duplicates, because repeated `FITXA_ID` values disappear after "
            "exact de-duplication. This should be encoded as a reproducible "
            "cleaning rule in Milestone 2."
        ),
    ]
    return "\n\n".join(sections)


def main() -> int:
    args = parse_args()
    frame = add_observed_dates(read_csv(args.csv_path))
    report = build_report(frame, args.csv_path)
    args.report_path.parent.mkdir(parents=True, exist_ok=True)
    args.report_path.write_text(report + "\n", encoding="utf-8")
    print(f"Wrote quality notes: {args.report_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
