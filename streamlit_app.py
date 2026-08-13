"""Streamlit interface for Barcelona Urban Life Signals."""

from __future__ import annotations

import os
from pathlib import Path

LOCAL_CACHE_DIR = Path("data/processed/.cache").resolve()
MPL_CACHE_DIR = LOCAL_CACHE_DIR / "matplotlib"
MPL_CACHE_DIR.mkdir(parents=True, exist_ok=True)
os.environ.setdefault("MPLCONFIGDIR", str(MPL_CACHE_DIR))
os.environ.setdefault("XDG_CACHE_HOME", str(LOCAL_CACHE_DIR))

import pandas as pd
import streamlit as st


DATA_PATH = Path("data/processed/iris_2025_clean.csv")
HERO_PATH = Path("assets/barcelona-urban-life-signals-hero.png")


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
def load_data(path: Path) -> pd.DataFrame:
    frame = pd.read_csv(
        path,
        parse_dates=["registration_date", "closure_date"],
        low_memory=False,
    )
    frame["weekday"] = frame["registration_date"].dt.day_name()
    frame["month"] = frame["registration_date"].dt.to_period("M").astype(str)
    return frame


def require_data() -> pd.DataFrame | None:
    if DATA_PATH.is_file():
        return load_data(DATA_PATH)

    st.error("The processed IRIS dataset is missing.")
    st.markdown(
        "Run these commands first:\n\n"
        "```bash\n"
        "python -m src.data_catalog --download efc9fd4d-a812-427c-846d-a086d22012a4\n"
        "python -m src.prepare_iris_dataset "
        "data/raw/2025_IRIS_Peticions_Ciutadanes_OpenData.csv\n"
        "```"
    )
    return None


def filter_frame(frame: pd.DataFrame) -> pd.DataFrame:
    st.sidebar.header("Read the city")
    st.sidebar.caption("Filters operate on registration date and reported fields.")

    min_date = frame["registration_date"].min().date()
    max_date = frame["registration_date"].max().date()
    selected_dates = st.sidebar.date_input(
        "Registration date range",
        value=(min_date, max_date),
        min_value=min_date,
        max_value=max_date,
    )
    if len(selected_dates) == 2:
        start_date, end_date = selected_dates
    else:
        start_date, end_date = min_date, max_date

    areas = st.sidebar.multiselect(
        "Request areas",
        options=sorted(frame["area"].dropna().unique()),
        placeholder="All areas",
    )
    districts = st.sidebar.multiselect(
        "Districts",
        options=sorted(frame["district"].dropna().unique()),
        placeholder="All districts",
    )
    supports = st.sidebar.multiselect(
        "Channels",
        options=sorted(frame["support"].dropna().unique()),
        placeholder="All channels",
    )

    filtered = frame.loc[
        (frame["registration_date"].dt.date >= start_date)
        & (frame["registration_date"].dt.date <= end_date)
    ].copy()
    if areas:
        filtered = filtered.loc[filtered["area"].isin(areas)]
    if districts:
        filtered = filtered.loc[filtered["district"].isin(districts)]
    if supports:
        filtered = filtered.loc[filtered["support"].isin(supports)]

    return filtered


def metric_row(frame: pd.DataFrame) -> None:
    daily = frame.groupby("registration_date").size()
    missing_geo = frame["district"].isna().mean() * 100 if len(frame) else 0
    median_lag = frame["closure_lag_days"].median() if len(frame) else 0

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Requests", f"{len(frame):,}")
    col2.metric("Median daily volume", f"{int(daily.median()) if len(daily) else 0:,}")
    col3.metric("Median closure lag", f"{int(median_lag)} days")
    col4.metric("Missing district", f"{missing_geo:.1f}%")


def daily_chart(frame: pd.DataFrame) -> None:
    daily = (
        frame.groupby("registration_date", as_index=False)
        .size()
        .rename(columns={"size": "requests"})
        .sort_values("registration_date")
    )
    daily["7-day average"] = daily["requests"].rolling(7, min_periods=1).mean()
    st.line_chart(
        daily,
        x="registration_date",
        y=["requests", "7-day average"],
        height=360,
    )


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


def bar_chart(series: pd.Series, title: str) -> None:
    chart_data = series.rename_axis("category").reset_index(name="requests")
    st.subheader(title)
    st.bar_chart(chart_data, x="category", y="requests", height=320)


def closure_lag_histogram(frame: pd.DataFrame) -> None:
    clipped_lag = frame["closure_lag_days"].clip(upper=60)
    bins = pd.cut(clipped_lag, bins=range(0, 65, 5), include_lowest=True)
    histogram = bins.value_counts().sort_index()
    chart_data = pd.DataFrame(
        {
            "lag_bucket": histogram.index.astype(str),
            "requests": histogram.values,
        }
    )
    st.bar_chart(chart_data, x="lag_bucket", y="requests", height=340)
    st.caption("Lag values above 60 days are clipped into the last visible range.")


def volume_lag_scatter(frame: pd.DataFrame) -> None:
    chart_data = daily_metrics(frame)
    chart_data = chart_data.loc[chart_data["requests"] >= 25]
    st.scatter_chart(
        chart_data,
        x="requests",
        y="median_closure_lag_days",
        color="missing_district_percent",
        height=360,
    )
    st.caption(
        "Each point is a registration day with at least 25 requests. Colour shows missing district percentage."
    )


def district_area_mix(frame: pd.DataFrame) -> None:
    geocoded = frame.dropna(subset=["district"])
    if geocoded.empty:
        st.warning("No district information is available in the current filters.")
        return

    top_districts = geocoded["district"].value_counts().head(10).index
    top_areas = geocoded["area"].value_counts().head(8).index
    focused = geocoded.loc[
        geocoded["district"].isin(top_districts) & geocoded["area"].isin(top_areas)
    ]
    mix = focused.pivot_table(
        index="district",
        columns="area",
        values="fitxa_id",
        aggfunc="count",
        fill_value=0,
    ).reindex(index=top_districts, columns=top_areas)
    mix = mix.div(mix.sum(axis=1), axis=0).fillna(0) * 100
    st.dataframe(
        mix.style.format("{:.1f}%").background_gradient(cmap="YlGnBu"),
        width="stretch",
    )
    st.caption(
        "Rows are normalised within district, so this compares composition rather than raw district volume."
    )


def support_mix_by_area(frame: pd.DataFrame) -> None:
    if frame.empty:
        st.warning("No records match the current filters.")
        return

    top_areas = frame["area"].value_counts().head(8).index
    top_supports = frame["support"].value_counts().head(5).index
    focused = frame.loc[
        frame["area"].isin(top_areas) & frame["support"].isin(top_supports)
    ]
    mix = focused.pivot_table(
        index="area",
        columns="support",
        values="fitxa_id",
        aggfunc="count",
        fill_value=0,
    ).reindex(index=top_areas, columns=top_supports)
    mix = mix.div(mix.sum(axis=1), axis=0).fillna(0) * 100
    chart_data = (
        mix.reset_index()
        .melt(id_vars="area", var_name="support", value_name="share")
        .sort_values(["area", "support"])
    )
    st.bar_chart(chart_data, x="area", y="share", color="support", height=380)
    st.caption(
        "Channel mix is a reporting-behaviour signal. It can reflect access and habits, not only issue volume."
    )


def interpretation(frame: pd.DataFrame) -> None:
    daily = frame.groupby("registration_date").size()
    daily_signal = daily_metrics(frame)
    active_daily_signal = daily_signal.loc[daily_signal["requests"] >= 25]
    volume_lag_corr = active_daily_signal["requests"].corr(
        active_daily_signal["median_closure_lag_days"]
    )
    weekday = (
        frame.groupby("weekday")
        .size()
        .sort_values(ascending=False)
    )
    area = frame["area"].value_counts()

    if frame.empty:
        st.warning("No records match the current filters.")
        return

    st.markdown("### Statistical reading")
    st.markdown(
        f"""
        - The filtered view contains **{len(frame):,} reported requests**.
        - Median daily volume is **{int(daily.median()):,}**, while the highest
          day reaches **{int(daily.max()):,}**. That gap is the first anomaly
          hunting surface.
        - The most active weekday is **{weekday.index[0]}**, useful for separating
          civic reporting rhythm from true urban pressure.
        - The largest request area is **{area.index[0]}**, representing
          **{area.iloc[0] / len(frame) * 100:.1f}%** of the filtered records.
        - On active days, the correlation between request volume and median
          closure lag is **{volume_lag_corr:.2f}**. Treat this as an association
          to investigate, not as evidence that volume causes slower resolution.
        - These are reported citizen signals. They should be interpreted as
          behaviour visible through council reporting channels, not complete
          ground truth about the city.
        """
    )


def main() -> None:
    st.markdown(
        """
        <div class="signal-hero">
          <div class="signal-eyebrow">Barcelona Urban Life Signals</div>
          <div class="signal-title">Civic rhythm, weather pressure, city behaviour.</div>
          <div class="signal-copy">
            A first interface for reading reported citizen activity through
            dates, neighbourhood context, request areas, and reporting channels.
            The goal is to surface patterns before claiming explanations.
          </div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    if HERO_PATH.is_file():
        st.image(str(HERO_PATH), width="stretch")

    frame = require_data()
    if frame is None:
        return

    filtered = filter_frame(frame)
    metric_row(filtered)

    tab1, tab2, tab3, tab4, tab5, tab6, tab7, tab8 = st.tabs(
        [
            "Daily rhythm",
            "Weekday",
            "Request areas",
            "Geography",
            "Closure lag",
            "Scatter",
            "District mix",
            "Channels",
        ]
    )
    with tab1:
        st.subheader("Reported activity by registration date")
        daily_chart(filtered)
    with tab2:
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
            filtered["weekday"].value_counts().reindex(weekday_order).fillna(0)
        )
        bar_chart(weekday_counts, "Reported activity by weekday")
    with tab3:
        bar_chart(filtered["area"].value_counts().head(12), "Top request areas")
    with tab4:
        districts = (
            filtered["district"]
            .fillna("(missing geography)")
            .value_counts()
            .head(12)
        )
        bar_chart(districts, "District distribution")
    with tab5:
        st.subheader("Closure lag histogram")
        closure_lag_histogram(filtered)
    with tab6:
        st.subheader("Daily volume versus median closure lag")
        volume_lag_scatter(filtered)
    with tab7:
        st.subheader("Request-area mix by district")
        district_area_mix(filtered)
    with tab8:
        st.subheader("Reporting-channel mix by request area")
        support_mix_by_area(filtered)

    interpretation(filtered)

    st.caption(
        "IRIS records are reported citizen activity. Missing geography and "
        "reporting-channel differences are part of the signal and should not be hidden."
    )


if __name__ == "__main__":
    main()
