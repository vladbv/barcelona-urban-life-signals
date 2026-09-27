"""Streamlit interface for Barcelona Urban Life Signals."""

from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path

LOCAL_CACHE_DIR = Path("data/processed/.cache").resolve()
MPL_CACHE_DIR = LOCAL_CACHE_DIR / "matplotlib"
MPL_CACHE_DIR.mkdir(parents=True, exist_ok=True)
os.environ.setdefault("MPLCONFIGDIR", str(MPL_CACHE_DIR))
os.environ.setdefault("XDG_CACHE_HOME", str(LOCAL_CACHE_DIR))

import pandas as pd
import streamlit as st

from src.iris_signals import (
    COHORT_NOTE, START, END, MISSING, category_summary, closure_histogram,
    composition_counts, composition_shares, daily_metrics, read_prepared,
    registration_cohort, volume_lag_correlation, weekday_summary,
)


DATA_PATH = Path("data/processed/iris_2025_clean.csv")


st.set_page_config(
    page_title="Barcelona Urban Life Signals",
    page_icon="🏙️",
    layout="wide",
)


st.markdown(
    """
    <style>
    :root {
        --terracotta: #b84a3a;
        --vermell: #9f1d35;
        --mar: #174c5e;
        --rajola: #e7b65c;
        --paper: #fff8ef;
    }
    .stApp {
        background:
            radial-gradient(circle at top left, rgba(231,182,92,.22), transparent 30%),
            linear-gradient(180deg, #fff8ef 0%, #f7efe3 52%, #efe1ce 100%);
    }
    .block-container {
        padding-top: 2rem;
        max-width: 1180px;
    }
    .signal-hero {
        border: 1px solid rgba(23, 76, 94, .18);
        border-radius: 28px;
        padding: 1.35rem 1.5rem;
        background: rgba(255, 248, 239, .82);
        box-shadow: 0 18px 45px rgba(69, 41, 23, .11);
    }
    .signal-eyebrow {
        color: var(--vermell);
        font-weight: 800;
        letter-spacing: .12em;
        text-transform: uppercase;
        font-size: .82rem;
    }
    .signal-title {
        color: var(--mar);
        font-size: clamp(2.2rem, 5vw, 4.4rem);
        line-height: .94;
        font-weight: 900;
        margin: .2rem 0 .75rem;
    }
    .signal-copy {
        color: #49372c;
        max-width: 760px;
        font-size: 1.04rem;
    }
    div[data-testid="stMetric"] {
        background: rgba(255, 255, 255, .64);
        border: 1px solid rgba(23, 76, 94, .15);
        border-radius: 18px;
        padding: .85rem 1rem;
        box-shadow: 0 10px 24px rgba(69, 41, 23, .08);
    }
    h2, h3 {
        color: var(--mar);
    }
    </style>
    """,
    unsafe_allow_html=True,
)


@st.cache_data(show_spinner=False)
def load_data(path: Path, modified_ns: int, size_bytes: int) -> pd.DataFrame:
    # File identity arguments invalidate cached data after a regenerated CSV.
    frame = read_prepared(path)
    with path.open("rb") as stream:
        frame.attrs["source_sha256"] = hashlib.file_digest(stream, "sha256").hexdigest()
    return frame


def matching_report(source_hash: str) -> bytes | None:
    """Only offer the full-year report when it was generated from this snapshot."""
    try:
        manifest = json.loads(Path("reports/iris_analysis_manifest.json").read_text(encoding="utf-8"))
        if manifest["processed_input"]["sha256"] == source_hash:
            return Path("reports/iris_exploration.html").read_bytes()
    except (OSError, ValueError, KeyError, TypeError):
        pass
    return None


def require_data() -> pd.DataFrame | None:
    if not DATA_PATH.is_file():
        st.error("The processed IRIS dataset is missing.")
        st.code(
            "python -m src.data_catalog --download efc9fd4d-a812-427c-846d-a086d22012a4\n"
            "python -m src.inspect_data data/raw/2025_IRIS_Peticions_Ciutadanes_OpenData.csv\n"
            "python -m src.prepare_iris_dataset data/raw/2025_IRIS_Peticions_Ciutadanes_OpenData.csv",
            language="bash",
        )
        return None
    try:
        stat = DATA_PATH.stat()
        return load_data(DATA_PATH, stat.st_mtime_ns, stat.st_size)
    except (ValueError, OSError) as error:
        st.error(f"The processed file did not pass validation: {error}")
        return None


def filter_frame(frame: pd.DataFrame):
    st.sidebar.header("Explore the observed cohort")
    st.sidebar.caption("Records registered and closed in 2025. Filters apply to every tab.")
    dates = st.sidebar.date_input(
        "Registration date range", value=(START.date(), END.date()),
        min_value=START.date(), max_value=END.date(),
    )
    choices = {}
    for column, label in [("area", "Request areas"), ("district", "Districts"), ("support", "Channels")]:
        choices[column] = st.sidebar.multiselect(
            label, sorted(frame[column].fillna(MISSING).unique()), placeholder="All",
        )
    if len(dates) != 2:
        st.info("Select an end date to complete the registration range.")
        return None
    start, end = map(pd.Timestamp, dates)
    if start > end:
        st.warning("Choose a start date on or before the end date.")
        return None
    filtered = frame.loc[frame["registration_date"].between(start, end)].copy()
    for column, values in choices.items():
        if values:
            filtered = filtered.loc[filtered[column].fillna(MISSING).isin(values)]
    return filtered, start, end


def download_table(table: pd.DataFrame, name: str, label: str = "Download this table") -> None:
    st.download_button(
        label, table.to_csv(index=False).encode("utf-8"),
        file_name=f"iris_filtered_{name}.csv", mime="text/csv", key=f"download_{name}",
    )


def show_mix(frame: pd.DataFrame, row: str, column: str, top_columns: int) -> None:
    counts = composition_counts(frame, row, column, top_rows=10, top_columns=top_columns)
    if counts.empty:
        st.info("No records with district information are available in this selection.")
        return
    shares = composition_shares(counts)
    st.dataframe(shares.style.format("{:.1f}%").background_gradient(cmap="YlGnBu"), width="stretch")
    st.caption("Each row includes all records in the displayed group. Other / missing retains the categories outside the displayed leaders.")
    download_table(shares.reset_index(), f"{row}_{column}_shares")
    download_table(counts.reset_index(), f"{row}_{column}_counts", "Download underlying counts")


def main() -> None:
    st.markdown(
        '<div class="signal-hero"><div class="signal-eyebrow">Barcelona Urban Life Signals</div>'
        '<div class="signal-title">What citizen reports make visible.</div>'
        '<div class="signal-copy">Read reporting rhythms, request areas, and geographic coverage '
        'through the inspected 2025 IRIS export.</div></div>', unsafe_allow_html=True,
    )
    frame = require_data()
    if frame is None:
        return
    cohort = registration_cohort(frame)
    st.info(COHORT_NOTE)
    st.caption(
        f"Local snapshot: {len(frame):,} deduplicated records; {len(cohort):,} in the headline cohort. "
        f"The {len(frame) - len(cohort):,} earlier registrations remain in the processed file."
    )
    selection = filter_frame(cohort)
    if selection is None:
        return
    filtered, start, end = selection
    if filtered.empty:
        st.warning("No records match these filters. Widen the date range or clear a category filter.")
        return
    daily = daily_metrics(filtered, start, end)
    weekday = weekday_summary(daily)
    areas = category_summary(filtered, "area")
    missing = filtered["district"].isna().mean() * 100
    lag = filtered["closure_lag_days"]
    st.caption(f"Current selection: {start.date()} to {end.date()} · {len(daily)} calendar days · {len(filtered):,} observed records")
    columns = st.columns(4)
    for column, label, value in zip(columns,
        ["Observed requests", "Mean per calendar day", "Median recorded closure lag", "Missing district"],
        [f"{len(filtered):,}", f"{daily['requests'].mean():,.1f}", f"{lag.median():g} days", f"{missing:.1f}%"]):
        column.metric(label, value)

    overview, time_tab, areas_tab, geography, closure, data_tab = st.tabs([
        "Read the findings", "Time", "Areas & channels", "Geography", "Recorded closure", "Data & methods",
    ])
    with overview:
        st.subheader("What this selection shows")
        leading = areas.iloc[0]
        st.markdown(
            f"**{leading['area']}** is the largest request area: **{leading['requests']:,} records "
            f"({leading['share_percent']:.1f}%)**. **{missing:.1f}%** of selected records lack a district. "
            f"The median recorded closure lag is **{lag.median():g} days**, and the 95th percentile is "
            f"**{lag.quantile(.95):.1f} days**."
        )
        st.markdown(
            "These readings describe reported activity in the selected completed records. "
            "Category and channel differences can reflect reporting habits and municipal processes. "
            "Neither report counts nor recorded closure dates establish issue severity or successful resolution."
        )
        st.warning(
            "Late-year declines can reflect the requirement to close by 31 December. "
            "Comparisons of published request-type labels such as INCIDENCIA and ISSUE "
            "over time need a validated mapping; see the monthly labels in Data & methods."
        )
        report = matching_report(frame.attrs["source_sha256"])
        if report is not None:
            st.download_button(
                "Download the full-year illustrated report (all records, independent of filters)",
                report, file_name="iris_exploration.html", mime="text/html",
            )
            st.caption("The standalone report includes explanations, 13 plots, aggregate CSV downloads, and methods. It opens offline.")
        else:
            st.caption("Generate the full-year report for this data snapshot with: python -m src.explore_iris_signals")

    with time_tab:
        st.subheader("Observed reports by registration date")
        chart_daily = daily.rename(columns={
            "registration_date": "Registration date", "requests": "Observed requests",
            "rolling_7_day": "7-day average",
        })
        st.line_chart(chart_daily, x="Registration date", y=["Observed requests", "7-day average"], height=340)
        st.caption("The 7-day average uses seven complete calendar days in this selection. Zero-record days are included; no estimate is made of reports absent from the export.")
        st.subheader("Average reports per weekday")
        st.bar_chart(weekday.dropna(subset=["mean_daily_requests"]), x="weekday", y="mean_daily_requests", sort=False)
        st.caption("Divide by the number of each weekday in the selected date range; a weekday outside that range is undefined.")
        st.dataframe(weekday, hide_index=True, width="stretch")
        download_table(daily, "daily")
        download_table(weekday, "weekday")

    with areas_tab:
        st.subheader("Request areas and their share of this selection")
        st.bar_chart(areas.head(12), x="area", y="requests", horizontal=True, sort=False)
        st.dataframe(areas, hide_index=True, width="stretch")
        download_table(areas, "areas")
        st.subheader("Reporting-channel composition by request area")
        show_mix(filtered, "area", "support", 5)
        st.caption("Channels can reflect access, habits, request mix, and administrative routing. They are descriptive groups here, not causal explanations.")

    with geography:
        districts = category_summary(filtered, "district")
        st.subheader("District coverage, including missing values")
        st.bar_chart(districts, x="district", y="requests", horizontal=True, sort=False)
        st.subheader("Where district information is missing")
        st.dataframe(areas[["area", "requests", "missing_district_rows", "missing_district_percent"]], hide_index=True, width="stretch")
        st.subheader("Request-area composition within each known district")
        show_mix(filtered.dropna(subset=["district"]), "district", "area", 8)
        st.caption("These are shares among published records with a district, not population-adjusted rates. Missing-district records may include requests that do not refer to a specific place.")
        download_table(districts, "districts")

    with closure:
        histogram = closure_histogram(filtered)
        st.subheader("Calendar days until recorded closure")
        st.bar_chart(histogram, x="lag_days", y="requests", sort=False)
        st.caption(f"Unequal-width groups; >60 retains every longer lag. Maximum in this selection: {lag.max():g} days. Administrative closure is not proof of resolution.")
        scatter = daily.dropna(subset=["median_closure_lag_days"])
        st.subheader("Daily volume and median recorded lag")
        st.scatter_chart(scatter, x="requests", y="median_closure_lag_days", color="missing_district_percent")
        corr = volume_lag_correlation(daily)
        st.caption(
            f"Pearson r = {corr:.2f}; {len(scatter)} observed days. All days with defined lag are included."
            if corr is not None else "Correlation is not estimable: need at least three days with variation in both measures."
        )
        st.caption("No adjustment for request mix, calendar, or closure-year selection. This association does not establish that higher volume causes slower closure.")
        download_table(histogram, "closure_lag")

    with data_tab:
        st.subheader("Inspect the records behind the selection")
        st.caption(f"First {min(200, len(filtered))} of {len(filtered):,} records in the current selection; preview is not a random sample.")
        st.dataframe(filtered.head(200), hide_index=True, width="stretch")
        st.subheader("Published request-type labels")
        types = category_summary(filtered, "request_type")
        st.dataframe(types, hide_index=True, width="stretch")
        download_table(types, "request_types")
        type_months = pd.crosstab(
            filtered["registration_date"].dt.to_period("M").astype(str),
            filtered["request_type"].fillna(MISSING),
        ).rename_axis("month").reset_index()
        st.dataframe(type_months, hide_index=True, width="stretch")
        download_table(type_months, "request_type_monthly")
        st.markdown(
            "Source labels are preserved as published. Apparent translations need publisher "
            "confirmation before merging; the table above helps identify changes over time. "
            "A published label does not identify the language used by the reporting citizen. "
            "No crosswalk is applied."
        )
        st.markdown(
            "**Methods:** exact duplicate rows removed; both published dates retained; no geographic "
            "imputation or category merging. Date filters use registration date. Daily means include "
            "all calendar days in the selected range. Composition denominators include smaller and "
            "missing categories. Raw downloads remain unchanged."
        )
        st.markdown("[Source: Open Data BCN — IRIS](https://opendata-ajuntament.barcelona.cat/data/en/dataset/iris)")
        st.caption("The date and ID checks run whenever a changed processed input is loaded. Input fingerprints and full-year methods are recorded in reports/iris_analysis_manifest.json.")


if __name__ == "__main__":
    main()
