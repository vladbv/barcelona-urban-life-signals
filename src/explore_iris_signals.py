"""Generate reproducible charts, aggregate CSVs and an offline IRIS reading guide."""

from __future__ import annotations

import argparse
import os
import textwrap
from pathlib import Path

os.environ.setdefault("MPLCONFIGDIR", str(Path("data/processed/.matplotlib-cache").resolve()))

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from matplotlib.ticker import StrMethodFormatter

from src.iris_signals import WEEKDAYS, build_tables, read_prepared, volume_lag_correlation

DEFAULT_INPUT_PATH = Path("data/processed/iris_2025_clean.csv")
BARCELONA = {
    "sea": "#174C5E", "tile": "#E6A23C", "terracotta": "#B84A3A",
    "vermell": "#8C2F39", "green": "#2B7A78", "paper": "#FFF8EF",
    "ink": "#2F241D", "grid": "#D8BFA6",
}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("input_path", nargs="?", type=Path, default=DEFAULT_INPUT_PATH)
    parser.add_argument("--figures-dir", type=Path, default=Path("reports/figures"))
    parser.add_argument("--tables-dir", type=Path, default=Path("data/processed/summaries"))
    parser.add_argument("--report-path", type=Path, default=Path("reports/iris_signal_summary.md"))
    parser.add_argument("--html-path", type=Path, default=Path("reports/iris_exploration.html"))
    parser.add_argument("--manifest-path", type=Path, default=Path("reports/iris_analysis_manifest.json"))
    parser.add_argument(
        "--readme-path", type=Path,
        help="also refresh the marked plot interpretations in this README (for example README.md)",
    )
    return parser.parse_args()


def style_axis(ax: plt.Axes, title: str, xlabel: str = "", ylabel: str = "") -> None:
    ax.set_title(title, loc="left", pad=18, color=BARCELONA["ink"], fontweight="bold")
    ax.set_xlabel(xlabel)
    ax.set_ylabel(ylabel)
    ax.grid(color=BARCELONA["grid"], alpha=.3, linewidth=.8)
    ax.set_axisbelow(True)
    ax.set_facecolor("#FFFCF7")
    ax.spines[["top", "right"]].set_visible(False)


def save(fig: plt.Figure, directory: Path, name: str, note: str = "") -> Path:
    footer = "IRIS local export · Registered and closed in 2025 · Counts describe observed reports."
    if note:
        footer += "\n" + note
    fig.text(.02, .015, footer, color=BARCELONA["ink"], fontsize=8, va="bottom")
    fig.set_facecolor(BARCELONA["paper"])
    fig.tight_layout(rect=(0, .075 if note else .05, 1, 1))
    path = directory / f"iris_{name}.png"
    fig.savefig(path, dpi=150)
    plt.close(fig)
    return path


def wrapped(values, width: int = 32) -> list[str]:
    return [textwrap.fill(str(value), width) for value in values]


def horizontal_bars(table: pd.DataFrame, category: str, title: str, directory: Path, name: str) -> Path:
    table = table.head(12).iloc[::-1]
    fig, ax = plt.subplots(figsize=(11.5, 7))
    ax.barh(wrapped(table[category]), table["requests"], color=BARCELONA["green"])
    for i, (_, row) in enumerate(table.iterrows()):
        ax.text(row["requests"], i, f"  {row['requests']:,} ({row['share_percent']:.1f}%)", va="center", fontsize=8)
    style_axis(ax, title, "Observed requests")
    ax.set_xlim(0, table["requests"].max() * 1.3)
    ax.xaxis.set_major_formatter(StrMethodFormatter("{x:,.0f}"))
    return save(fig, directory, name, "Percentages use all records in the headline cohort as denominator.")


def heatmap(table: pd.DataFrame, title: str, label: str, directory: Path, name: str, note: str, percent: bool = False) -> Path:
    fig, ax = plt.subplots(figsize=(13, 7.5))
    image = ax.imshow(table.values, cmap="YlGnBu", aspect="auto", vmin=0)
    ax.set_title(title, loc="left", pad=18, fontweight="bold", color=BARCELONA["ink"])
    ax.set_xticks(range(len(table.columns)), wrapped(table.columns, 17), fontsize=8)
    ax.set_yticks(range(len(table)), table.index, fontsize=9)
    maximum = np.nanmax(table.values)
    for y in range(len(table)):
        for x in range(len(table.columns)):
            value = table.iloc[y, x]
            label_text = "<1%" if percent and 0 < value < 1 else f"{value:.0f}{'%' if percent else ''}"
            ax.text(x, y, label_text, ha="center", va="center",
                    fontsize=8, color="white" if value > maximum * .55 else BARCELONA["ink"])
    fig.colorbar(image, ax=ax, shrink=.8, label=label)
    return save(fig, directory, name, note)


def create_figures(tables: dict[str, pd.DataFrame], directory: Path) -> dict[str, Path]:
    directory.mkdir(parents=True, exist_ok=True)
    figures = {}
    daily = tables["daily"]
    fig, ax = plt.subplots(figsize=(12, 5.5))
    ax.plot(daily["registration_date"], daily["requests"], color=BARCELONA["tile"], alpha=.5, lw=1, label="Daily records")
    ax.plot(daily["registration_date"], daily["rolling_7_day"], color=BARCELONA["sea"], lw=2.5, label="Trailing 7 calendar days")
    style_axis(ax, "A weekly reporting rhythm within the observed cohort", "Registration date", "Observed requests")
    ax.set_ylim(bottom=0)
    ax.legend(frameon=False)
    figures["daily"] = save(fig, directory, "daily_registration_volume", "Late-year records must close by 31 December to appear here; the year-end decline is not a demand estimate.")

    weekday = tables["weekday"]
    fig, ax = plt.subplots(figsize=(10, 5.5))
    bars = ax.bar(weekday["weekday"].str[:3], weekday["mean_daily_requests"], color=[BARCELONA["sea"]] * 5 + [BARCELONA["tile"]] * 2)
    ax.bar_label(bars, fmt="%.0f", padding=4)
    style_axis(ax, "Reporting is more frequent on weekdays", "", "Mean observed requests per calendar day")
    ax.set_ylim(0, weekday["mean_daily_requests"].max() * 1.15)
    figures["weekday"] = save(fig, directory, "weekday_pattern", "Each total is divided by the number of that weekday in 2025 (52 or 53 days).")

    figures["areas"] = horizontal_bars(tables["areas"], "area", "Which request areas appear most often?", directory, "top_request_areas")
    figures["districts"] = horizontal_bars(tables["districts"], "district", "Missing district is part of the distribution", directory, "district_distribution")

    fig, ax = plt.subplots(figsize=(10, 5.5))
    lag = tables["closure_lag"]
    bars = ax.bar(lag["lag_days"].astype(str), lag["requests"], color=BARCELONA["vermell"])
    ax.bar_label(bars, fmt="{:,.0f}", padding=4, fontsize=8)
    style_axis(ax, "Recorded closure lags have a long tail", "Calendar days from registration to recorded closure (unequal-width groups)", "Observed requests")
    ax.set_ylim(0, lag["requests"].max() * 1.15)
    figures["lag"] = save(fig, directory, "closure_lag_histogram", "The >60 bucket contains every longer lag. Recorded closure does not establish that an issue was resolved.")

    fig, ax = plt.subplots(figsize=(10, 6))
    observed = daily.dropna(subset=["median_closure_lag_days"])
    dots = ax.scatter(observed["requests"], observed["median_closure_lag_days"], c=observed["missing_district_percent"], cmap="YlGnBu", s=30, alpha=.8)
    corr = volume_lag_correlation(daily)
    ax.text(.02, .97, f"Pearson r = {corr:.2f}\nn = {len(observed)} observed days" if corr is not None else "Correlation not estimable", transform=ax.transAxes, va="top")
    style_axis(ax, "Daily volume and recorded closure lag", "Observed requests registered that day", "Median recorded closure lag (days)")
    fig.colorbar(dots, ax=ax, label="Missing district (%)")
    figures["scatter"] = save(fig, directory, "daily_volume_vs_closure_lag", "All days with observed requests; no volume threshold. Descriptive association, with no causal interpretation.")

    calendar = daily.pivot_table(index="weekday", columns="month", values="requests", aggfunc="mean").reindex(WEEKDAYS)
    calendar.columns = [pd.Timestamp(month).strftime("%b") for month in calendar.columns]
    figures["calendar"] = heatmap(calendar, "Calendar pattern within one observed year", "Mean observed requests / calendar day", directory, "month_weekday_heatmap", "Zero-record days are included. A single closure-selected year cannot establish recurring seasonality.")

    areas = tables["areas"].head(12).sort_values("median_closure_lag_days")
    fig, ax = plt.subplots(figsize=(12, 7.5))
    ax.hlines(range(len(areas)), 0, areas["median_closure_lag_days"], color=BARCELONA["grid"])
    ax.scatter(areas["median_closure_lag_days"], range(len(areas)), s=areas["requests"] / areas["requests"].max() * 700 + 50, color=BARCELONA["sea"])
    ax.set_yticks(range(len(areas)), wrapped(areas["area"]))
    for y, (_, row) in enumerate(areas.iterrows()):
        ax.annotate(f"{row['requests']:,}", (row["median_closure_lag_days"], y), xytext=(18, 0), textcoords="offset points", va="center", fontsize=8)
    style_axis(ax, "Closure lags differ across request areas", "Median recorded closure lag (days)")
    ax.set_xlim(0, areas["median_closure_lag_days"].max() * 1.35)
    figures["area_lag"] = save(fig, directory, "area_volume_vs_lag", "Dot size and labels show record counts. Different request areas represent different administrative processes.")

    figures["district_mix"] = heatmap(tables["district_area_shares"].set_index("district"), "Request-area composition among records with a district", "Share of all records in district (%)", directory, "district_area_mix_heatmap", "Other / missing retains every remaining request area. No population or reporting-rate adjustment.", percent=True)

    mix = tables["area_channel_shares"].set_index("area").iloc[::-1]
    fig, ax = plt.subplots(figsize=(12, 7.5))
    left = np.zeros(len(mix))
    colors = [BARCELONA[k] for k in ["sea", "terracotta", "tile", "green", "vermell"]] + ["#B8B0A5"]
    for column, color in zip(mix, colors):
        ax.barh(wrapped(mix.index), mix[column], left=left, label=column, color=color)
        left += mix[column].to_numpy()
    style_axis(ax, "Reporting channels vary by request area", "Share of all records in request area (%)")
    ax.set_xlim(0, 100)
    ax.legend(loc="upper center", bbox_to_anchor=(.5, -.12), ncol=2, frameon=False, fontsize=8)
    figures["channels"] = save(fig, directory, "support_mix_by_area", "Other / missing retains all channels outside the five most frequent; each row totals 100%.")

    geo = tables["areas"].head(10).iloc[::-1]
    fig, ax = plt.subplots(figsize=(12, 7))
    bars = ax.barh(wrapped(geo["area"]), geo["missing_district_percent"], color=BARCELONA["terracotta"])
    ax.bar_label(bars, labels=[f"{v:.1f}%" for v in geo["missing_district_percent"]], padding=5, fontsize=9)
    style_axis(ax, "Geographic coverage depends on the request area", "Records missing district (%)")
    ax.set_xlim(0, 115)
    figures["missingness"] = save(fig, directory, "geography_coverage", "Ten largest areas. A missing district may reflect a non-place-specific request; do not assign one by imputation.")

    monthly = tables["monthly"]
    fig, axes = plt.subplots(2, 1, figsize=(12, 8), sharex=True)
    x = np.arange(len(monthly))
    axes[0].bar(x, monthly["mean_daily_requests"], color=BARCELONA["sea"])
    style_axis(axes[0], "The year-end cutoff limits which requests appear", ylabel="Mean records / calendar day")
    axes[1].plot(x, monthly["p95_closure_lag_days"], marker="o", color=BARCELONA["terracotta"], label="Observed 95th percentile lag")
    axes[1].plot(x, monthly["median_closure_lag_days"], marker="o", color=BARCELONA["green"], label="Observed median lag")
    style_axis(axes[1], "", "Registration month", "Recorded closure lag (days)")
    axes[1].set_xticks(x, [pd.Timestamp(m).strftime("%b") for m in monthly["month"]])
    axes[1].set_ylim(bottom=0)
    axes[1].legend(frameon=False, fontsize=9)
    axes[1].text(.98, .95, "A 1 Dec registration can contribute at most 30 days of lag.\nA 31 Dec registration can contribute only 0 days.", transform=axes[1].transAxes, ha="right", va="top", fontsize=9)
    figures["selection"] = save(fig, directory, "cohort_selection", "Declines can reflect the closure-year selection. These charts do not establish falling demand or faster service.")

    types = tables["request_type_monthly"].set_index("month")
    types = types.div(types.sum(axis=1), axis=0).mul(100).T
    types.columns = [pd.Timestamp(month).strftime("%b") for month in types.columns]
    figures["types"] = heatmap(types, "Published request-type labels change during the year", "Share of observed records in month (%)", directory, "request_type_labels", "Source labels are preserved. Do not read INCIDENCIA declining and ISSUE rising as a change in reported issue type.", percent=True)
    return figures


def main() -> int:
    from src.iris_report import write_reports

    args = parse_args()
    try:
        frame = read_prepared(args.input_path)
    except ValueError as error:
        raise SystemExit(str(error)) from error
    tables = build_tables(frame)
    args.tables_dir.mkdir(parents=True, exist_ok=True)
    for name, table in tables.items():
        table.to_csv(args.tables_dir / f"iris_{name}.csv", index=False, float_format="%.6f")
    figures = create_figures(tables, args.figures_dir)
    write_reports(frame, tables, figures, args)
    print(f"Wrote {len(figures)} figures: {args.figures_dir}")
    print(f"Wrote {len(tables)} aggregate tables: {args.tables_dir}")
    print(f"Wrote reading guide: {args.report_path}")
    print(f"Wrote standalone report: {args.html_path}")
    print(f"Wrote reproducibility manifest: {args.manifest_path}")
    if args.readme_path is not None:
        print(f"Updated README plot interpretations: {args.readme_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
