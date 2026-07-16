"""Create a focused profile report for an observed IRIS CSV export."""

from __future__ import annotations

import argparse
from pathlib import Path

import pandas as pd


DEFAULT_REPORT_PATH = Path("reports/iris_profile.md")
DEFAULT_DAILY_OUTPUT_PATH = Path("data/processed/iris_daily_requests.csv")

DATE_PARTS = {
    "registration_date": ("ANY_DATA_ALTA", "MES_DATA_ALTA", "DIA_DATA_ALTA"),
    "closure_date": (
        "ANY_DATA_TANCAMENT",
        "MES_DATA_TANCAMENT",
        "DIA_DATA_TANCAMENT",
    ),
}
CLASSIFICATION_COLUMNS = [
    "TIPUS",
    "AREA",
    "ELEMENT",
    "DETALL",
    "DISTRICTE",
    "BARRI",
    "SUPORT",
]
GEOGRAPHY_COLUMNS = [
    "CODI_DISTRICTE",
    "DISTRICTE",
    "CODI_BARRI",
    "BARRI",
    "SECCIO_CENSAL",
    "COORDENADA_X",
    "COORDENADA_Y",
    "LONGITUD",
    "LATITUD",
]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Profile the observed Open Data BCN IRIS CSV and write a small "
            "Markdown report plus daily request counts."
        )
    )
    parser.add_argument("csv_path", type=Path, help="path to the raw IRIS CSV")
    parser.add_argument(
        "--report-path",
        type=Path,
        default=DEFAULT_REPORT_PATH,
        help=f"Markdown report path (default: {DEFAULT_REPORT_PATH})",
    )
    parser.add_argument(
        "--daily-output-path",
        type=Path,
        default=DEFAULT_DAILY_OUTPUT_PATH,
        help=f"daily volume CSV path (default: {DEFAULT_DAILY_OUTPUT_PATH})",
    )
    return parser.parse_args()


def read_csv(csv_path: Path) -> pd.DataFrame:
    if not csv_path.is_file():
        raise SystemExit(f"File not found: {csv_path}")
    return pd.read_csv(csv_path, low_memory=False)


def build_date(frame: pd.DataFrame, parts: tuple[str, str, str]) -> pd.Series:
    year_column, month_column, day_column = parts
    missing = [
        column
        for column in (year_column, month_column, day_column)
        if column not in frame.columns
    ]
    if missing:
        raise ValueError(f"Missing date part columns: {', '.join(missing)}")

    values = frame[[year_column, month_column, day_column]].rename(
        columns={year_column: "year", month_column: "month", day_column: "day"}
    )
    return pd.to_datetime(values, errors="coerce")


def add_observed_dates(frame: pd.DataFrame) -> pd.DataFrame:
    enriched = frame.copy()
    for output_column, parts in DATE_PARTS.items():
        enriched[output_column] = build_date(enriched, parts)
    return enriched


def markdown_table(frame: pd.DataFrame) -> str:
    if frame.empty:
        return "_No rows._"

    text_frame = frame.fillna("").astype(str)
    headers = list(text_frame.columns)
    rows = text_frame.values.tolist()
    widths = [
        max(len(header), *(len(row[index]) for row in rows))
        for index, header in enumerate(headers)
    ]

    def format_row(values: list[str]) -> str:
        cells = [
            f" {value.ljust(widths[index])} "
            for index, value in enumerate(values)
        ]
        return "|" + "|".join(cells) + "|"

    separator = "|" + "|".join(f" {'-' * width} " for width in widths) + "|"
    return "\n".join([format_row(headers), separator, *[format_row(row) for row in rows]])


def top_values(frame: pd.DataFrame, column: str, limit: int = 10) -> pd.DataFrame:
    counts = (
        frame[column]
        .fillna("(missing)")
        .value_counts(dropna=False)
        .head(limit)
        .rename_axis(column)
        .reset_index(name="rows")
    )
    counts["percent"] = (counts["rows"] / len(frame) * 100).round(2)
    return counts


def missingness(frame: pd.DataFrame, columns: list[str]) -> pd.DataFrame:
    observed_columns = [column for column in columns if column in frame.columns]
    return pd.DataFrame(
        {
            "column": observed_columns,
            "missing_rows": [int(frame[column].isna().sum()) for column in observed_columns],
            "missing_percent": [
                round(float(frame[column].isna().mean() * 100), 2)
                for column in observed_columns
            ],
        }
    )


def create_daily_counts(frame: pd.DataFrame) -> pd.DataFrame:
    daily = (
        frame.dropna(subset=["registration_date"])
        .groupby("registration_date", as_index=False)
        .size()
        .rename(columns={"registration_date": "date", "size": "requests"})
    )
    daily["date"] = daily["date"].dt.date
    return daily


def describe_dates(frame: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for column in ["registration_date", "closure_date"]:
        series = frame[column]
        rows.append(
            {
                "date_field": column,
                "valid_rows": int(series.notna().sum()),
                "missing_or_invalid_rows": int(series.isna().sum()),
                "min_date": series.min().date() if series.notna().any() else None,
                "max_date": series.max().date() if series.notna().any() else None,
            }
        )
    return pd.DataFrame(rows)


def duplicate_summary(frame: pd.DataFrame) -> pd.DataFrame:
    rows = [{"duplicate_type": "exact_full_row", "rows": int(frame.duplicated().sum())}]
    if "FITXA_ID" in frame.columns:
        rows.append(
            {
                "duplicate_type": "repeated_fitxa_id",
                "rows": int(frame["FITXA_ID"].duplicated().sum()),
            }
        )
    return pd.DataFrame(rows)


def build_report(
    frame: pd.DataFrame,
    csv_path: Path,
    daily_output_path: Path,
    observed_column_count: int,
) -> str:
    date_summary = describe_dates(frame)
    duplicate_rows = duplicate_summary(frame)
    geography_missingness = missingness(frame, GEOGRAPHY_COLUMNS)

    classification_sections = []
    for column in CLASSIFICATION_COLUMNS:
        if column in frame.columns:
            classification_sections.append(
                f"### Top `{column}` values\n\n{markdown_table(top_values(frame, column))}"
            )

    return "\n\n".join(
        [
            "# IRIS data profile",
            "Generated from the locally downloaded Open Data BCN IRIS CSV.",
            "## Source file",
            f"- Path: `{csv_path}`",
            f"- Rows: {len(frame):,}",
            f"- Observed CSV columns: {observed_column_count:,}",
            f"- Derived profiling columns: {len(DATE_PARTS):,}",
            "## Date coverage",
            markdown_table(date_summary),
            "## Duplicate indicators",
            markdown_table(duplicate_rows),
            "## Geographic missingness",
            markdown_table(geography_missingness),
            "## Main classification distributions",
            "\n\n".join(classification_sections),
            "## Generated outputs",
            f"- Daily registration counts: `{daily_output_path}`",
            "## Interpretation notes",
            (
                "- These counts describe reported citizen activity, not every "
                "urban issue that occurred."
            ),
            (
                "- Missing geography can reflect how a request was reported, "
                "classified, or published; it should not be treated as random "
                "without further checks."
            ),
            (
                "- Duplicate rows are flagged for review. This report does not "
                "remove them."
            ),
        ]
    )


def main() -> int:
    args = parse_args()
    raw_frame = read_csv(args.csv_path)
    frame = add_observed_dates(raw_frame)

    daily = create_daily_counts(frame)
    args.daily_output_path.parent.mkdir(parents=True, exist_ok=True)
    daily.to_csv(args.daily_output_path, index=False)

    report = build_report(
        frame,
        args.csv_path,
        args.daily_output_path,
        observed_column_count=len(raw_frame.columns),
    )
    args.report_path.parent.mkdir(parents=True, exist_ok=True)
    args.report_path.write_text(report + "\n", encoding="utf-8")

    print(f"Wrote report: {args.report_path}")
    print(f"Wrote daily counts: {args.daily_output_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
