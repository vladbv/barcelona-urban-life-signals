# Project plan

## Goal

Explore how citizen-reported activity in Barcelona relates to calendar,
weather, place, and city activity. Start with what the actual records support,
keep reporting behaviour and data selection explicit, and add models only
when they answer a defined question.

## Milestone 1 — Discover and understand IRIS

Status: complete for the preserved 2025 snapshot; live catalog rechecked 2026-09-27.

- [x] Establish a Python 3.11 environment and live catalog discovery command.
- [x] Select and download the 2025 CSV into `data/raw/` without modifying it.
- [x] Inspect its 25 observed columns, date coverage, missingness, and categories.
- [x] Record resource ID `efc9fd4d-a812-427c-846d-a086d22012a4` and provenance.
- [x] Investigate duplicate `FITXA_ID` values: repeated IDs disappear after exact
      row deduplication in this snapshot.
- [x] Identify closure-year selection: all observed closures occur in 2025;
      some registrations are earlier, and later closures are absent.
- [x] Revalidate the processed data against preparation of the original raw file.
- [x] Preserve source fingerprints and distinguish catalog availability from
      completeness or remote byte-for-byte equivalence.

Evidence: `reports/iris_catalog.md`, `iris_profile.md`, `iris_quality_notes.md`.
The raw file has 287,304 rows, 3,393 exact duplicates, and 5,284 earlier
registrations (5,283 after deduplication).

## Milestone 2 — Prepare an analysis dataset

Status: complete for descriptive analysis of the inspected snapshot.

- [x] Remove exact duplicate rows only; preserve missing geography and categories.
- [x] Retain both parsed dates with explicit names and check nonnegative lags.
- [x] Save prepared data under `data/processed/`, with documented column mapping.
- [x] Check IDs, date validity, cohort membership, and row reconciliation.
- [x] Decide category policy: preserve original request-type labels; do not merge
      apparent translations without a validated crosswalk.
- [x] Document the observed late-year source-label transition and expose it in a
      monthly table and plot.

Output: 283,911 processed records, including 278,628 registered and closed in
2025. Preparation notes: `reports/iris_prepare_summary.md`. Analysis decisions:
`reports/iris_category_decisions.md`.

## Milestone 3 — Make descriptive patterns visible and explainable

Status: complete for the current cohort, with coverage limitations explicit.

- [x] Plot daily reporting and weekday averages using full calendar exposure.
- [x] Show within-year month/weekday patterns without claiming recurring seasonality.
- [x] Compare observed request areas, recorded closure lags, and reporting channels.
- [x] Keep missing district visible and show its dependence on area and channel.
- [x] Retain Other / missing in composition denominators and export underlying counts.
- [x] Separate 2025 registrations from older registrations when reporting lag tails.
- [x] Show the closure-year cutoff's implications for late-year volume and lag.
- [x] Keep channels as descriptive groups; postpone a modelling feature decision
      until a specific prediction/association question and observation window exist.
- [x] Produce 13 static plots and 13 downloadable aggregate tables.
- [x] Generate a reading guide with observations, interpretations, limitations,
      and a one-minute explanation suitable for presenting the work.
- [x] Give every plot its own accessible interpretation, connecting the numbers
      to everyday civic concerns while keeping uncertainty explicit (ethos,
      logos, and pathos).
- [x] Show all 13 plots directly in the GitHub README, with individual reading
      instructions, explanations, and jump links; generate those passages from
      the same source as the Markdown and HTML reports.
- [x] Generate a standalone offline HTML report with embedded plots and CSVs.
- [x] Update the existing local viewer to use the same cohort and calculations,
      with missing-geography filters, data previews, and safe empty selections.
- [x] Add regression checks for sparse calendars, denominators, lag tails, input
      validation, and interface filtering.

Reproduce reports and README: `python -m src.explore_iris_signals --readme-path README.md`.
Explore: `python -m streamlit run streamlit_app.py`.
Verify: `python -m unittest discover -s tests -v`.

Reports: `reports/iris_signal_summary.md`, `reports/iris_exploration.html`,
`reports/iris_analysis_manifest.json`. Aggregate CSVs are generated into
`data/processed/summaries/`. Raw files remain unchanged.

## Before Milestone 4 — Establish comparable observation windows

Status: next, required before interpreting weather or year-end trends.

- [ ] Inspect adjacent closure-year exports, preserving and profiling each source
      before combining any records.
- [ ] Quantify how later closure files change the apparent registration cohort;
      unresolved requests may remain unobserved even after combining years.
- [ ] Define comparable follow-up windows for the chosen outcome and explain
      remaining selection. Do not assume all 2025 registrations are present.
- [ ] Validate request-type mappings against publisher documentation and inspect
      stability in area/element/detail fields before using category trends.

Exit criterion: a stated population, date convention, inclusion rule, and
follow-up window appropriate for a specific comparison.

## Milestone 4 — Add weather context

Status: not started; the descriptive report makes no weather-effect claims.

- [ ] Define a narrow question, with the request area, time scale, and outcome explicit.
- [ ] Select and inspect a reliable Barcelona weather source and station coverage.
- [ ] Align dates, missingness, and spatial/time resolution without imputing IRIS geography.
- [ ] Compare transparent summaries and calendar-aware regression baselines.
- [ ] Distinguish association from causation and examine reporting-channel composition.

## Later, only after the evidence supports it

- documented policy/event context after observation and weather baselines;
- anomaly detection and time-aware predictive evaluation;
- additional city-activity data;
- application polish and deployment.

Advanced models are not a prerequisite. Each addition must answer a specific
question better than a simpler analysis.
