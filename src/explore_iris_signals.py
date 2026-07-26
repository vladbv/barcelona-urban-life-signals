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


def save_closure_lag_histogram(frame: pd.DataFrame, figures_dir: Path) -> Path:
    lag_days = frame["closure_lag_days"].dropna()

    fig, ax = plt.subplots(figsize=(10, 5))
    ax.hist(
        lag_days.clip(upper=60),
        bins=30,
        color="#8C2F39",
        alpha=0.82,
        edgecolor="white",
    )
    ax.set_title("Closure lag distribution, clipped at 60 days")
    ax.set_xlabel("Days between registration and closure")
    ax.set_ylabel("Requests")
    ax.grid(axis="y", alpha=0.25)
    ax.text(
        0.98,
        0.86,
        f"Median: {int(lag_days.median())} days\n95th pct: {int(lag_days.quantile(0.95))} days\nMax: {int(lag_days.max())} days",
        transform=ax.transAxes,
        ha="right",
        va="top",
        bbox={"boxstyle": "round,pad=0.5", "facecolor": "#FFF8EF", "edgecolor": "#D8BFA6"},
    )
    fig.tight_layout()

    output_path = figures_dir / "iris_closure_lag_histogram.png"
    fig.savefig(output_path, dpi=160)
    plt.close(fig)
    return output_path


def daily_metrics(frame: pd.DataFrame) -> pd.DataFrame:
    return (
        frame.groupby("registration_date")
        .agg(
            requests=("fitxa_id", "count"),
            median_closure_lag_days=("closure_lag_days", "median"),
            missing_district_percent=("district", lambda values: values.isna().mean() * 100),
        )
        .reset_index()
        .sort_values("registration_date")
    )


def save_daily_volume_lag_scatter(frame: pd.DataFrame, figures_dir: Path) -> Path:
    daily = daily_metrics(frame)
    active_days = daily.loc[daily["requests"] >= 25].copy()

    fig, ax = plt.subplots(figsize=(9, 6))
    scatter = ax.scatter(
        active_days["requests"],
        active_days["median_closure_lag_days"],
        c=active_days["missing_district_percent"],
        cmap="viridis",
        s=34,
        alpha=0.78,
        edgecolor="white",
        linewidth=0.35,
    )
    ax.set_title("Daily volume versus median closure lag")
    ax.set_xlabel("Requests registered that day")
    ax.set_ylabel("Median closure lag, days")
    ax.grid(alpha=0.25)
    colorbar = fig.colorbar(scatter, ax=ax)
    colorbar.set_label("Missing district, %")
    fig.tight_layout()

    output_path = figures_dir / "iris_daily_volume_vs_closure_lag.png"
    fig.savefig(output_path, dpi=160)
    plt.close(fig)
    return output_path


def save_month_weekday_heatmap(frame: pd.DataFrame, figures_dir: Path) -> Path:
    active_2025 = frame.loc[frame["registration_date"].dt.year == 2025].copy()
    active_2025["month"] = active_2025["registration_date"].dt.strftime("%b")
    active_2025["weekday"] = active_2025["registration_date"].dt.day_name()

    weekday_order = [
        "Monday",
        "Tuesday",
        "Wednesday",
        "Thursday",
        "Friday",
        "Saturday",
        "Sunday",
    ]
    month_order = [
        "Jan",
        "Feb",
        "Mar",
        "Apr",
        "May",
        "Jun",
        "Jul",
        "Aug",
        "Sep",
        "Oct",
        "Nov",
        "Dec",
    ]
    heatmap = (
        active_2025.pivot_table(
            index="weekday",
            columns="month",
            values="fitxa_id",
            aggfunc="count",
            fill_value=0,
        )
        .reindex(index=weekday_order, columns=month_order)
        .fillna(0)
        .astype(int)
    )

    fig, ax = plt.subplots(figsize=(11, 5.5))
    image = ax.imshow(heatmap.values, cmap="YlOrBr", aspect="auto")
    ax.set_title("2025 registration rhythm by month and weekday")
    ax.set_xticks(range(len(month_order)), month_order)
    ax.set_yticks(range(len(weekday_order)), weekday_order)
    colorbar = fig.colorbar(image, ax=ax)
    colorbar.set_label("Requests")

    for row_index, weekday in enumerate(weekday_order):
        for column_index, month in enumerate(month_order):
            value = int(heatmap.loc[weekday, month])
            ax.text(
                column_index,
                row_index,
                f"{value // 1000}k" if value >= 1000 else str(value),
                ha="center",
                va="center",
                color="#2F241D",
                fontsize=8,
            )
    fig.tight_layout()

    output_path = figures_dir / "iris_month_weekday_heatmap.png"
    fig.savefig(output_path, dpi=160)
    plt.close(fig)
    return output_path


def save_area_volume_lag_scatter(frame: pd.DataFrame, figures_dir: Path) -> Path:
    area_metrics = (
        frame.groupby("area")
        .agg(
            requests=("fitxa_id", "count"),
            median_closure_lag_days=("closure_lag_days", "median"),
        )
        .sort_values("requests", ascending=False)
        .head(12)
        .reset_index()
    )

    fig, ax = plt.subplots(figsize=(10, 6))
    ax.scatter(
        area_metrics["requests"],
        area_metrics["median_closure_lag_days"],
        s=(area_metrics["requests"] / area_metrics["requests"].max()) * 650 + 80,
        color="#174C5E",
        alpha=0.72,
        edgecolor="white",
        linewidth=0.8,
    )
    for _, row in area_metrics.iterrows():
        ax.annotate(
            row["area"],
            (row["requests"], row["median_closure_lag_days"]),
            xytext=(6, 4),
            textcoords="offset points",
            fontsize=8,
        )
    ax.set_title("Top request areas: volume versus median closure lag")
    ax.set_xlabel("Requests")
    ax.set_ylabel("Median closure lag, days")
    ax.grid(alpha=0.25)
    fig.tight_layout()

    output_path = figures_dir / "iris_area_volume_vs_lag.png"
    fig.savefig(output_path, dpi=160)
    plt.close(fig)
    return output_path


def build_report(frame: pd.DataFrame, figure_paths: list[Path]) -> str:
    daily = frame.groupby("registration_date").size()
    daily_signal = daily_metrics(frame)
    active_daily_signal = daily_signal.loc[daily_signal["requests"] >= 25]
    volume_lag_corr = active_daily_signal["requests"].corr(
        active_daily_signal["median_closure_lag_days"]
    )
    weekday = (
        frame.assign(weekday=frame["registration_date"].dt.day_name())
        .groupby("weekday")
        .size()
        .sort_values(ascending=False)
    )
    lag_days = frame["closure_lag_days"].dropna()

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
            f"- Median closure lag: {int(lag_days.median())} days",
            f"- 95th percentile closure lag: {int(lag_days.quantile(0.95))} days",
            (
                "- Correlation between daily request volume and median closure "
                f"lag on active days: {volume_lag_corr:.2f}"
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
            (
                "- Scatter plots show association surfaces for follow-up "
                "questions; they are not causal estimates."
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
        save_closure_lag_histogram(frame, args.figures_dir),
        save_daily_volume_lag_scatter(frame, args.figures_dir),
        save_month_weekday_heatmap(frame, args.figures_dir),
        save_area_volume_lag_scatter(frame, args.figures_dir),
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
