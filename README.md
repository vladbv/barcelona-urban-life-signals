# Barcelona Urban Life Signals

**What can citizen requests tell us about Barcelona—and what do the records leave out?**

A Python project that turns Barcelona City Council’s public request records
into reproducible analysis. It examines reported concerns, reporting patterns
and missing information before drawing conclusions about city life.

**Python · pandas · Matplotlib · Streamlit · automated tests**

[Full analysis](reports/iris_signal_summary.md) ·
[Downloadable report](reports/iris_exploration.html) ·
[Run the project](REPRODUCING.md)

## The data, in plain terms

[IRIS, published by Open Data BCN](https://opendata-ajuntament.barcelona.cat/data/en/dataset/iris),
records contact with the council: incidents, complaints, inquiries, suggestions
and thanks. One row represents a request, not necessarily one person or one problem.

The preserved 2025 file contains **287,304 rows**. Removing **3,393 exact duplicates**
leaves **283,911 records**. The main analysis uses **278,628 requests registered
and marked closed in 2025**. Earlier registrations stay in the prepared data.

**Marked closed is an administrative status, not proof that an issue was fixed.**
Requests still open or closed in another year are missing from this view.

## Technical work you can inspect

- **Reproducible data preparation:** catalog discovery, preserved raw files,
  inspected schemas and validated dates and identifiers. [Preparation code](src/prepare_iris_dataset.py).
- **Careful comparisons:** full-calendar daily averages, explicit denominators
  and retained missing locations. [Analysis code](src/iris_signals.py).
- **Verifiable outputs:** source fingerprints, regression tests and charts
  regenerated from shared calculations. [Tests](tests/) · [Source manifest](reports/iris_analysis_manifest.json).

<!-- BEGIN IRIS PLOT READINGS -->

## Three findings

These charts use **278,628 requests registered and marked closed in 2025**. They describe contact with the council, not every problem in the city.

### 1. Cleaning and maintenance account for 56% of requests

![Request counts: cleaning 87,738; maintenance 68,491; all other topics 122,399.](reports/figures/iris_highlight_topics.png)

**156,229 requests concern the upkeep of shared public spaces.** The bars count requests by topic; “all other” combines the remaining categories.

Streets and pavements are part of everyday life. Their prominence identifies a concrete topic for further study. **More reports do not necessarily mean more severe problems:** several requests may concern the same issue.

### 2. Weekdays average 1.9 times as many requests as weekends

![Daily average requests: 879 on weekdays and 474 at weekends.](reports/figures/iris_highlight_weekdays.png)

**879 requests per weekday, compared with 474 per weekend day.** Each total is divided by the number of days in its group, so five weekdays are not compared directly with two weekend days.

When assessing a busy day, compare it with similar weekdays first. **This measures when requests enter IRIS**, not when problems begin or why people choose to report.

### 3. 31% of requests have no recorded district

![Requests with a district: 191,675; without a district: 86,953.](reports/figures/iris_highlight_location.png)

**A district-only map would leave out 86,953 requests.** Keeping those records visible prevents a partial map from looking like a complete account.

Some requests concern administrative services rather than a specific place. **Missing district does not automatically mean an error**, and district counts cannot rank neighbourhood quality.

[Explore all 13 plots, English category labels and detailed interpretations](reports/iris_signal_summary.md).

<!-- END IRIS PLOT READINGS -->

## A finding that changed the analysis

**December’s observed count rises by 34.2% when later closures are included.**
A separate 2026 export adds 5,331 requests registered in December 2025,
raising that month’s count from 15,600 to 20,931.

The practical lesson: a year-end decline can partly reflect the file’s closing
date rather than fewer concerns. The later snapshot contains closures through
**31 March 2026**; it still does not reveal every open request.
[See the comparison plot and the 30-day/90-day follow-up rules](reports/iris_observation_windows.md).

## Explore further

- **[All 13 IRIS plots](reports/iris_signal_summary.md):** request topics, districts,
  reporting channels and time until marked closed, with English reading labels.
- **[Housing cost and resident satisfaction](reports/neighbourhood_living.md):**
  a separate 2025 comparison of all 73 neighbourhoods. Official rent and survey
  satisfaction are limited proxies; small samples are flagged.
- **[Offline HTML report](reports/iris_exploration.html):** download and open it in
  a browser for charts and downloadable aggregate tables.

For adjustable date, district, topic and channel filters, run the existing
Streamlit explorer locally after following the [setup guide](REPRODUCING.md):

```bash
python -m streamlit run streamlit_app.py
```

The README charts are static images. The explorer provides the filters.

## Reproduce the work

Use **Python 3.11**. The [setup guide](REPRODUCING.md) covers installation,
source downloads and inspection. Raw and processed data are excluded from Git.
With the inspected data prepared locally:

```bash
python -m src.explore_iris_signals --readme-path README.md
python -m unittest discover -s tests -v
```

Current scope: descriptive analysis and data-quality checks. Next: inspect a
weather source for a narrowly defined comparison. No causal or forecasting
claims are made. [Project plan](PROJECT_PLAN.md).
