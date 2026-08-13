"""Create first exploratory charts from the prepared IRIS dataset."""

from __future__ import annotations

import argparse
import os
import textwrap
from pathlib import Path

import pandas as pd

LOCAL_CACHE_DIR = Path("data/processed/.cache").resolve()
MPL_CACHE_DIR = LOCAL_CACHE_DIR / "matplotlib"
MPL_CACHE_DIR.mkdir(parents=True, exist_ok=True)
os.environ.setdefault("MPLCONFIGDIR", str(MPL_CACHE_DIR))
os.environ.setdefault("XDG_CACHE_HOME", str(LOCAL_CACHE_DIR))

import matplotlib.pyplot as plt
from matplotlib.ticker import StrMethodFormatter


DEFAULT_INPUT_PATH = Path("data/processed/iris_2025_clean.csv")
DEFAULT_FIGURES_DIR = Path("reports/figures")
DEFAULT_REPORT_PATH = Path("reports/iris_signal_summary.md")
BARCELONA = {
    "sea": "#174C5E",
    "tile": "#E6A23C",
    "terracotta": "#B84A3A",
    "vermell": "#8C2F39",
    "green": "#2B7A78",
    "paper": "#FFF8EF",
    "ink": "#2F241D",
    "grid": "#D8BFA6",
}


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


def active_2025(frame: pd.DataFrame) -> pd.DataFrame:
    return frame.loc[frame["registration_date"].dt.year == 2025].copy()


def style_axis(ax: plt.Axes, title: str, xlabel: str = "", ylabel: str = "") -> None:
    ax.set_title(title, pad=14, color=BARCELONA["ink"], fontweight="bold")
    ax.set_xlabel(xlabel)
    ax.set_ylabel(ylabel)
    ax.grid(color=BARCELONA["grid"], alpha=0.32, linewidth=0.8)
    ax.set_facecolor("#FFFCF7")
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)


def format_count_axis(ax: plt.Axes, axis: str = "x") -> None:
    formatter = StrMethodFormatter("{x:,.0f}")
    if axis == "x":
        ax.xaxis.set_major_formatter(formatter)
    else:
        ax.yaxis.set_major_formatter(formatter)


def save_daily_volume_chart(frame: pd.DataFrame, figures_dir: Path) -> Path:
    frame = active_2025(frame)
    daily = (
        frame.groupby("registration_date", as_index=False)
        .size()
        .rename(columns={"size": "requests"})
        .sort_values("registration_date")
    )
    daily["rolling_7_day"] = daily["requests"].rolling(7, min_periods=1).mean()

    fig, ax = plt.subplots(figsize=(13, 5.6))
    ax.plot(
        daily["registration_date"],
        daily["requests"],
        color=BARCELONA["tile"],
        alpha=0.32,
        linewidth=1.1,
        label="Daily requests",
    )
    ax.plot(
        daily["registration_date"],
        daily["rolling_7_day"],
        color=BARCELONA["sea"],
        linewidth=2.6,
        label="7-day average",
    )
    style_axis(
        ax,
        "Reported citizen activity by registration date, 2025",
        "Registration date",
        "Requests",
    )
    format_count_axis(ax, "y")
    ax.legend(frameon=False)
    fig.autofmt_xdate()
    fig.tight_layout()

    output_path = figures_dir / "iris_daily_registration_volume.png"
    fig.savefig(output_path, dpi=160)
    plt.close(fig)
    return output_path


def save_weekday_chart(frame: pd.DataFrame, figures_dir: Path) -> Path:
    frame = active_2025(frame)
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

    fig, ax = plt.subplots(figsize=(9.5, 5.2))
    weekday_counts.plot(kind="bar", ax=ax, color=BARCELONA["terracotta"])
    style_axis(ax, "Reported activity by weekday, 2025", "", "Requests")
    format_count_axis(ax, "y")
    ax.tick_params(axis="x", rotation=0)
    fig.tight_layout()

    output_path = figures_dir / "iris_weekday_pattern.png"
    fig.savefig(output_path, dpi=160)
    plt.close(fig)
    return output_path


def save_top_areas_chart(frame: pd.DataFrame, figures_dir: Path) -> Path:
    frame = active_2025(frame)
    top_areas = frame["area"].value_counts().head(10).sort_values()

    fig, ax = plt.subplots(figsize=(11, 6.4))
    top_areas.plot(kind="barh", ax=ax, color=BARCELONA["green"])
    style_axis(ax, "Top reported request areas, 2025", "Requests", "")
    format_count_axis(ax, "x")
    fig.tight_layout()

    output_path = figures_dir / "iris_top_request_areas.png"
    fig.savefig(output_path, dpi=160)
    plt.close(fig)
    return output_path


def save_district_chart(frame: pd.DataFrame, figures_dir: Path) -> Path:
    frame = active_2025(frame)
    district_counts = (
        frame["district"].fillna("(missing geography)").value_counts().head(12).sort_values()
    )

    fig, ax = plt.subplots(figsize=(11, 6.4))
    district_counts.plot(kind="barh", ax=ax, color=BARCELONA["tile"])
    style_axis(ax, "Reported requests by district availability, 2025", "Requests", "")
    format_count_axis(ax, "x")
    fig.tight_layout()

    output_path = figures_dir / "iris_district_distribution.png"
    fig.savefig(output_path, dpi=160)
    plt.close(fig)
    return output_path


def save_closure_lag_histogram(frame: pd.DataFrame, figures_dir: Path) -> Path:
    frame = active_2025(frame)
    lag_days = frame["closure_lag_days"].dropna()

    fig, ax = plt.subplots(figsize=(11, 5.8))
    ax.hist(
        lag_days.clip(upper=60),
        bins=range(0, 63, 3),
        color=BARCELONA["vermell"],
        alpha=0.86,
        edgecolor="white",
    )
    style_axis(
        ax,
        "Closure lag distribution, 2025 registrations; clipped at 60 days",
        "Days between registration and closure",
        "Requests",
    )
    format_count_axis(ax, "y")
    ax.text(
        0.98,
        0.86,
        f"Median: {int(lag_days.median())} days\n95th pct: {int(lag_days.quantile(0.95))} days\nMax: {int(lag_days.max())} days",
        transform=ax.transAxes,
        ha="right",
        va="top",
        bbox={
            "boxstyle": "round,pad=0.5",
            "facecolor": BARCELONA["paper"],
            "edgecolor": BARCELONA["grid"],
        },
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
    daily = daily_metrics(active_2025(frame))
    active_days = daily.loc[daily["requests"] >= 100].copy()

    fig, ax = plt.subplots(figsize=(10, 6.2))
    scatter = ax.scatter(
        active_days["requests"],
        active_days["median_closure_lag_days"],
        c=active_days["missing_district_percent"],
        cmap="YlGnBu",
        s=42,
        alpha=0.82,
        edgecolor="white",
        linewidth=0.45,
    )
    if len(active_days) > 1:
        correlation = active_days["requests"].corr(
            active_days["median_closure_lag_days"]
        )
        ax.text(
            0.03,
            0.93,
            f"Active 2025 days\nr = {correlation:.2f}",
            transform=ax.transAxes,
            ha="left",
            va="top",
            bbox={
                "boxstyle": "round,pad=0.5",
                "facecolor": BARCELONA["paper"],
                "edgecolor": BARCELONA["grid"],
            },
        )
    style_axis(
        ax,
        "Daily volume versus median closure lag, active 2025 days",
        "Requests registered that day",
        "Median closure lag, days",
    )
    format_count_axis(ax, "x")
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
    active_2025["date"] = active_2025["registration_date"].dt.date

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
        active_2025.groupby(["date", "month", "weekday"], as_index=False)
        .size()
        .pivot_table(
            index="weekday",
            columns="month",
            values="size",
            aggfunc="mean",
        )
        .reindex(index=weekday_order, columns=month_order)
        .fillna(0)
    )

    fig, ax = plt.subplots(figsize=(11.5, 5.8))
    image = ax.imshow(heatmap.values, cmap="YlOrRd", aspect="auto")
    ax.set_title(
        "Average daily requests by month and weekday, 2025",
        pad=14,
        color=BARCELONA["ink"],
        fontweight="bold",
    )
    ax.set_xticks(range(len(month_order)), month_order)
    ax.set_yticks(range(len(weekday_order)), weekday_order)
    colorbar = fig.colorbar(image, ax=ax)
    colorbar.set_label("Average requests per day")

    for row_index, weekday in enumerate(weekday_order):
        for column_index, month in enumerate(month_order):
            value = int(round(heatmap.loc[weekday, month]))
            ax.text(
                column_index,
                row_index,
                f"{value:,}",
                ha="center",
                va="center",
                color="#2F241D",
                fontsize=7.6,
            )
    ax.set_facecolor("#FFFCF7")
    fig.tight_layout()

    output_path = figures_dir / "iris_month_weekday_heatmap.png"
    fig.savefig(output_path, dpi=160)
    plt.close(fig)
    return output_path


def save_area_volume_lag_scatter(frame: pd.DataFrame, figures_dir: Path) -> Path:
    frame = active_2025(frame)
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
    area_metrics["wrapped_area"] = area_metrics["area"].map(
        lambda value: "\n".join(textwrap.wrap(value, width=32))
    )
    area_metrics = area_metrics.sort_values("median_closure_lag_days")

    fig, ax = plt.subplots(figsize=(11.5, 7.4))
    y_positions = range(len(area_metrics))
    scatter = ax.scatter(
        area_metrics["median_closure_lag_days"],
        y_positions,
        s=(area_metrics["requests"] / area_metrics["requests"].max()) * 950 + 120,
        c=area_metrics["requests"],
        cmap="YlGnBu",
        alpha=0.86,
        edgecolor="white",
        linewidth=0.8,
    )
    for y_position, (_, row) in zip(y_positions, area_metrics.iterrows()):
        ax.hlines(
            y_position,
            0,
            row["median_closure_lag_days"],
            color=BARCELONA["grid"],
            linewidth=1.2,
            alpha=0.8,
        )
        ax.text(
            row["median_closure_lag_days"] + 0.25,
            y_position,
            f"{int(row['requests']):,}",
            va="center",
            fontsize=8,
            color=BARCELONA["ink"],
        )
    ax.set_yticks(list(y_positions), area_metrics["wrapped_area"])
    style_axis(
        ax,
        "Top request areas: median closure lag and volume, 2025",
        "Median closure lag, days",
        "",
    )
    ax.set_xlim(left=0)
    colorbar = fig.colorbar(scatter, ax=ax)
    colorbar.set_label("Requests")
    fig.tight_layout()

    output_path = figures_dir / "iris_area_volume_vs_lag.png"
    fig.savefig(output_path, dpi=160)
    plt.close(fig)
    return output_path


def save_district_area_share_heatmap(frame: pd.DataFrame, figures_dir: Path) -> Path:
    frame = active_2025(frame).dropna(subset=["district"])
    top_districts = frame["district"].value_counts().head(10).index
    top_areas = frame["area"].value_counts().head(8).index
    focused = frame.loc[
        frame["district"].isin(top_districts) & frame["area"].isin(top_areas)
    ].copy()

    heatmap = focused.pivot_table(
        index="district",
        columns="area",
        values="fitxa_id",
        aggfunc="count",
        fill_value=0,
    ).reindex(index=top_districts, columns=top_areas)
    heatmap = heatmap.div(heatmap.sum(axis=1), axis=0).fillna(0) * 100

    wrapped_areas = [
        "\n".join(textwrap.wrap(area, width=18))
        for area in heatmap.columns
    ]

    fig, ax = plt.subplots(figsize=(12.5, 7.4))
    image = ax.imshow(heatmap.values, cmap="YlGnBu", aspect="auto")
    ax.set_title(
        "Request-area mix by district, 2025 records with geography",
        pad=14,
        color=BARCELONA["ink"],
        fontweight="bold",
    )
    ax.set_xticks(range(len(wrapped_areas)), wrapped_areas)
    ax.set_yticks(range(len(heatmap.index)), heatmap.index)
    ax.tick_params(axis="x", labelsize=8)
    colorbar = fig.colorbar(image, ax=ax)
    colorbar.set_label("Share within district, %")

    for row_index, district in enumerate(heatmap.index):
        for column_index, area in enumerate(heatmap.columns):
            value = heatmap.loc[district, area]
            if value >= 4:
                ax.text(
                    column_index,
                    row_index,
                    f"{value:.0f}%",
                    ha="center",
                    va="center",
                    color=BARCELONA["ink"],
                    fontsize=7.2,
                )
    ax.set_facecolor("#FFFCF7")
    fig.tight_layout()

    output_path = figures_dir / "iris_district_area_mix_heatmap.png"
    fig.savefig(output_path, dpi=160)
    plt.close(fig)
    return output_path


def save_support_mix_by_area(frame: pd.DataFrame, figures_dir: Path) -> Path:
    frame = active_2025(frame)
    top_areas = frame["area"].value_counts().head(8).index
    top_supports = frame["support"].value_counts().head(5).index
    focused = frame.loc[
        frame["area"].isin(top_areas) & frame["support"].isin(top_supports)
    ].copy()

    support_mix = focused.pivot_table(
        index="area",
        columns="support",
        values="fitxa_id",
        aggfunc="count",
        fill_value=0,
    ).reindex(index=top_areas, columns=top_supports)
    support_mix = support_mix.div(support_mix.sum(axis=1), axis=0).fillna(0) * 100

    wrapped_areas = [
        "\n".join(textwrap.wrap(area, width=34))
        for area in support_mix.index
    ]
    colors = [
        BARCELONA["sea"],
        BARCELONA["terracotta"],
        BARCELONA["tile"],
        BARCELONA["green"],
        BARCELONA["vermell"],
    ]

    fig, ax = plt.subplots(figsize=(11.8, 7.2))
    left = pd.Series(0.0, index=support_mix.index)
    for support, color in zip(support_mix.columns, colors):
        values = support_mix[support]
        ax.barh(wrapped_areas, values, left=left, color=color, label=support)
        left = left + values

    style_axis(
        ax,
        "Reporting-channel mix by top request area, 2025",
        "Share within request area, %",
        "",
    )
    ax.set_xlim(0, 100)
    ax.legend(
        frameon=False,
        loc="lower center",
        bbox_to_anchor=(0.5, -0.18),
        ncol=3,
    )
    fig.tight_layout()

    output_path = figures_dir / "iris_support_mix_by_area.png"
    fig.savefig(output_path, dpi=160)
    plt.close(fig)
    return output_path


def build_report(frame: pd.DataFrame, figure_paths: list[Path]) -> str:
    active_frame = active_2025(frame)
    daily = active_frame.groupby("registration_date").size()
    daily_signal = daily_metrics(active_frame)
    active_daily_signal = daily_signal.loc[daily_signal["requests"] >= 100]
    volume_lag_corr = active_daily_signal["requests"].corr(
        active_daily_signal["median_closure_lag_days"]
    )
    weekday = (
        active_frame.assign(weekday=active_frame["registration_date"].dt.day_name())
        .groupby("weekday")
        .size()
        .sort_values(ascending=False)
    )
    lag_days = active_frame["closure_lag_days"].dropna()
    geocoded = active_frame.dropna(subset=["district"])
    geocoded_share = len(geocoded) / len(active_frame) * 100

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
            f"- 2025 registration rows used for headline charts: {len(active_frame):,}",
            (
                f"- 2025 registration-date range: "
                f"{active_frame['registration_date'].min().date()} to "
                f"{active_frame['registration_date'].max().date()}"
            ),
            f"- Median daily requests: {int(daily.median()):,}",
            f"- Highest daily requests: {int(daily.max()):,}",
            f"- Most active weekday in this export: {weekday.index[0]}",
            (
                f"- Top request area: "
                f"{active_frame['area'].value_counts().index[0]}"
            ),
            f"- Median closure lag: {int(lag_days.median())} days",
            f"- 95th percentile closure lag: {int(lag_days.quantile(0.95))} days",
            f"- 2025 records with district information: {geocoded_share:.1f}%",
            (
                "- Correlation between daily request volume and median closure "
                f"lag on active days: {volume_lag_corr:.2f}"
            ),
            "## Figures",
            "\n".join(f"- `{path}`" for path in figure_paths),
            "## Notes",
            (
                "- The headline charts focus on records registered in 2025, "
                "because the source export is closure-year oriented and contains "
                "a small number of older registrations."
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
            (
                "- Channel-mix charts are reporting-behaviour signals. They may "
                "reflect access, habits, and municipal workflow, not only the "
                "underlying urban issue."
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
        save_district_area_share_heatmap(frame, args.figures_dir),
        save_support_mix_by_area(frame, args.figures_dir),
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
