"""Create first exploratory charts from the prepared IRIS dataset."""

from __future__ import annotations

import argparse
import os
from pathlib import Path

import pandas as pd

LOCAL_CACHE_DIR = Path("data/processed/.cache").resolve()
MPL_CACHE_DIR = LOCAL_CACHE_DIR / "matplotlib"
MPL_CACHE_DIR.mkdir(parents=True, exist_ok=True)
os.environ.setdefault("MPLCONFIGDIR", str(MPL_CACHE_DIR))
os.environ.setdefault("XDG_CACHE_HOME", str(LOCAL_CACHE_DIR))

import matplotlib.pyplot as plt


DEFAULT_INPUT_PATH = Path("data/processed/iris_2025_clean.csv")
DEFAULT_FIGURES_DIR = Path("reports/figures")
DEFAULT_REPORT_PATH = Path("reports/iris_signal_summary.md")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Create first static charts for Barcelona IRIS urban signals."
    )
    parser.add_argument(
        "input_path",
        nargs="?",
        type=Path,
        default=DEFAULT_INPUT_PATH,
        help=f"processed IRIS CSV path (default: {DEFAULT_INPUT_PATH})",
    )
    parser.add_argument(
        "--figures-dir",
        type=Path,
        default=DEFAULT_FIGURES_DIR,
        help=f"figure output directory (default: {DEFAULT_FIGURES_DIR})",
    )
    parser.add_argument(
        "--report-path",
        type=Path,
        default=DEFAULT_REPORT_PATH,
        help=f"Markdown summary path (default: {DEFAULT_REPORT_PATH})",
    )
    return parser.parse_args()


def read_prepared(input_path: Path) -> pd.DataFrame:
    if not input_path.is_file():
        raise SystemExit(
            f"File not found: {input_path}. Run src.prepare_iris_dataset first."
        )
    frame = pd.read_csv(
        input_path,
        parse_dates=["registration_date", "closure_date"],
        low_memory=False,
    )
    return frame


def save_daily_volume_chart(frame: pd.DataFrame, figures_dir: Path) -> Path:
    daily = (
        frame.groupby("registration_date", as_index=False)
        .size()
        .rename(columns={"size": "requests"})
        .sort_values("registration_date")
    )
    daily["rolling_7_day"] = daily["requests"].rolling(7, min_periods=1).mean()

    fig, ax = plt.subplots(figsize=(12, 5))
    ax.plot(
        daily["registration_date"],
        daily["requests"],
        color="#D95F02",
        alpha=0.28,
        linewidth=1,
        label="Daily requests",
    )
    ax.plot(
        daily["registration_date"],
        daily["rolling_7_day"],
        color="#1B4D5C",
        linewidth=2,
        label="7-day average",
    )
    ax.set_title("Reported citizen activity by registration date")
    ax.set_xlabel("Registration date")
    ax.set_ylabel("Requests")
    ax.legend()
    ax.grid(axis="y", alpha=0.25)
    fig.autofmt_xdate()
    fig.tight_layout()

    output_path = figures_dir / "iris_daily_registration_volume.png"
    fig.savefig(output_path, dpi=160)
    plt.close(fig)
    return output_path


def save_weekday_chart(frame: pd.DataFrame, figures_dir: Path) -> Path:
    weekday_order = [
        "Monday",
        "Tuesday",
        "Wednesday",
        "Thursday",
        "Friday",
        "Saturday",
        "Sunday",
    ]
    weekday_counts = (
        frame.assign(weekday=frame["registration_date"].dt.day_name())
        .groupby("weekday")
        .size()
        .reindex(weekday_order)
    )

    fig, ax = plt.subplots(figsize=(9, 5))
    weekday_counts.plot(kind="bar", ax=ax, color="#B84A62")
    ax.set_title("Reported activity by weekday")
    ax.set_xlabel("")
    ax.set_ylabel("Requests")
    ax.grid(axis="y", alpha=0.25)
    fig.tight_layout()

    output_path = figures_dir / "iris_weekday_pattern.png"
    fig.savefig(output_path, dpi=160)
    plt.close(fig)
    return output_path


def save_top_areas_chart(frame: pd.DataFrame, figures_dir: Path) -> Path:
    top_areas = frame["area"].value_counts().head(10).sort_values()

    fig, ax = plt.subplots(figsize=(10, 6))
    top_areas.plot(kind="barh", ax=ax, color="#2B7A78")
    ax.set_title("Top reported request areas")
    ax.set_xlabel("Requests")
    ax.set_ylabel("")
    ax.grid(axis="x", alpha=0.25)
    fig.tight_layout()

    output_path = figures_dir / "iris_top_request_areas.png"
    fig.savefig(output_path, dpi=160)
    plt.close(fig)
    return output_path


def save_district_chart(frame: pd.DataFrame, figures_dir: Path) -> Path:
    district_counts = (
        frame["district"].fillna("(missing geography)").value_counts().head(12).sort_values()
    )

    fig, ax = plt.subplots(figsize=(10, 6))
    district_counts.plot(kind="barh", ax=ax, color="#E6A23C")
    ax.set_title("Reported requests by district availability")
    ax.set_xlabel("Requests")
    ax.set_ylabel("")
    ax.grid(axis="x", alpha=0.25)
    fig.tight_layout()

    output_path = figures_dir / "iris_district_distribution.png"
    fig.savefig(output_path, dpi=160)
    plt.close(fig)
    return output_path


def build_report(frame: pd.DataFrame, figure_paths: list[Path]) -> str:
    daily = frame.groupby("registration_date").size()
    weekday = (
        frame.assign(weekday=frame["registration_date"].dt.day_name())
        .groupby("weekday")
        .size()
        .sort_values(ascending=False)
    )

    return "\n\n".join(
        [
            "# First IRIS signal summary",
            (
                "This is a first visual pass over reported citizen activity. "
                "It describes reporting patterns, not complete city conditions "
                "or causal effects."
            ),
            "## Quick readings",
            f"- Processed rows: {len(frame):,}",
            (
                f"- Registration-date range: "
                f"{frame['registration_date'].min().date()} to "
                f"{frame['registration_date'].max().date()}"
            ),
            f"- Median daily requests: {int(daily.median()):,}",
            f"- Highest daily requests: {int(daily.max()):,}",
            f"- Most active weekday in this export: {weekday.index[0]}",
            (
                f"- Top request area: "
                f"{frame['area'].value_counts().index[0]}"
            ),
            "## Figures",
            "\n".join(f"- `{path}`" for path in figure_paths),
            "## Notes",
            (
                "- Because the 2025 file is closure-year oriented, registration "
                "dates before 2025 are visible in the early part of the daily "
                "chart."
            ),
            (
                "- District charts include missing geography explicitly instead "
                "of hiding it."
            ),
            (
                "- Category language variants are not normalised yet, so request "
                "type comparisons should wait until that decision is documented."
            ),
        ]
    )


def main() -> int:
    args = parse_args()
    frame = read_prepared(args.input_path)
    args.figures_dir.mkdir(parents=True, exist_ok=True)

    figure_paths = [
        save_daily_volume_chart(frame, args.figures_dir),
        save_weekday_chart(frame, args.figures_dir),
        save_top_areas_chart(frame, args.figures_dir),
        save_district_chart(frame, args.figures_dir),
    ]

    report = build_report(frame, figure_paths)
    args.report_path.parent.mkdir(parents=True, exist_ok=True)
    args.report_path.write_text(report + "\n", encoding="utf-8")

    print(f"Wrote signal summary: {args.report_path}")
    for path in figure_paths:
        print(f"Wrote figure: {path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
