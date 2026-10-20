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

Status: observation-window audit complete for the preserved 2025 export and
2026 snapshot downloaded on 2026-10-02. Type-label mapping remains unverified.

- [x] Preserve and inspect the adjacent 2026 closure export: 72,326 rows, 25
      matching columns, 1,452 exact duplicates, 70,874 unique records.
- [x] Check cross-export identities, dates, and closure lags before combining.
- [x] Quantify the 6,419 additional 2025 registrations, including 5,331 in December.
- [x] Establish 30-day and 90-day inclusive follow-up definitions; mask dates
      without enough observed follow-up rather than treating them as zero.
- [x] Inspect publisher field definitions and exact category labels. The catalog
      does not supply a value crosswalk; retain original request-type labels.
- [ ] Obtain a publisher-validated mapping before using translated request-type
      trends. This remains outside the narrower category-based weather question.

The later snapshot ends on 2026-03-31, despite its October download date.
All 365 dates in 2025 satisfy both follow-up date rules, but source completeness
and still-open requests remain unknown. The defined outcome is a count of
observed requests closed within a fixed period, not complete demand or a
closure success rate. Shared category names do not certify unchanged meaning.

Evidence: `reports/iris_observation_windows.md`, `iris_2026_profile.md`, and
`iris_observation_manifest.json`. Reproduce with `python -m src.audit_iris_observation`.
The original 2025 explorer and 13-plot tour remain a separate comparison.

## Milestone 4 — Add weather context

Status: narrow question defined; source discovery and modelling not started.

- [x] Define the first question: daily weather and observed cleaning/collection
      requests registered in 2025 and closed within 30 days, with 90-day sensitivity.
      Exclude unverified request-type mappings and distinguish this selected count
      from complete demand.
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

## Requested addition — neighbourhood housing cost and satisfaction

Status: exploratory 2025 comparison complete (2026-10-06).

- [x] Make plot 9 bilingual with English reading labels and original categories.
- [x] Inspect official annual rent workbook and survey fields/codebooks before joining.
- [x] Match all 73 neighbourhoods; use survey weights and exclude nonresponses.
- [x] Publish the four requested quadrants with median boundaries, a full name table,
      source fingerprints and explicit small-sample flags.
- [x] Explain that housing rent and neighbourhood satisfaction are limited proxies;
      these estimates are not official neighbourhood rankings or IRIS-derived measures.

Reproduce with `python -m src.neighbourhood_quadrants --download` (downloads only
missing originals), or omit `--download` for an offline rebuild. No dependencies
added. The existing weather milestone remains separate.

## Reading-guide clarity update — 2026-10-13

- [x] Use concrete titles across the 13-plot tour and explain requests as entries
      submitted to the council, including reports, inquiries and suggestions.
- [x] Add English reading labels beside published category names throughout the
      category charts, preserving the original data and category distinctions.
- [x] Explain district percentages with a simple example and state that they do
      not rank district or neighbourhood quality.
- [x] Define time until marked closed using dates, distinguish administrative
      closure from resolution, and explain longer times without relying on jargon.

The shared interpretations continue to pair numerical evidence (logos), clear
sources and limitations (ethos), and concrete relevance to residents (pathos).
Rebuild README, plots and reports with the existing exploration command.

## Portfolio overview — 2026-10-14

- [x] Put source, observation unit, sample selection and technical evidence before plots.
- [x] Reduce the README to three findings with large English labels, direct values
      and one limitation beside each interpretation.
- [x] Keep all 13 detailed readings and the neighbourhood comparison in linked reports.
- [x] Move installation, acquisition and reproduction details to REPRODUCING.md.
- [x] Generate selected README charts from the existing validated summary tables;
      the normal rebuild preserves the shorter overview.

The daily-series title and reading now name the council, year, source and counted
unit explicitly. Reviewed all 13 titles; retain the other plain-language titles
in the full report. README images stay static; existing Streamlit filters provide
adjustable views. No new dependencies, datasets or modelling scope.

## Course-to-project explanation — 2026-10-16

- [x] Connect the author’s stated Master’s training to inspectable preparation,
      descriptive analysis, observation checks and reproducibility.
- [x] Document a proposed Bayesian count-model question and distinguish it from
      implemented work in `reports/course_to_project.md`.
- [x] After source and calendar checks, assess whether a count model adds value:
      state assumptions, check prior sensitivity and predictive fit, and evaluate
      later dates with closure outcomes available at each training cutoff.

This update changes documentation only. No Bayesian model, forecast, clustering
or new data transformation is introduced. Course exercises and reference materials
remain separate from the repository’s implemented results.

## Requested modelling extension — 2026-10-16

The documentation-only proposal above is now implemented following the request
to demonstrate actual Machine Learning and Bayesian Learning skills.

- [x] Define daily observed cleaning requests marked closed within 30 days;
      retain zero-count calendar days and repeat with a 90-day definition.
- [x] Fit a weekday-average baseline, independent weekday Gamma–Poisson models
      and a fixed shallow decision tree using existing dependencies.
- [x] Evaluate October–December 2025 with training labels matured before October 1.
      State that historical publication availability cannot be reconstructed.
- [x] Publish prior, likelihood and posterior plots, predictive coverage,
      posterior predictive dispersion checks and prior sensitivity.
- [x] Explain poor interval coverage and the tree’s reversal in the 90-day check;
      retain those failures as evidence rather than tune against the test quarter.
- [x] Add reproducible commands, source/settings manifest and model boundary tests.

See `reports/iris_model_comparison.md`. This narrow retrospective benchmark is
separate from the unfinished weather-source milestone. Any further model choices
need validation inside training data and fresh evaluation data before operational
claims. No neural network or additional dependency was needed.

## Model stability check — 2026-10-19

- [x] Apply expanding-window temporal validation within January–August using
      April, June and August validation months fixed before computing scores.
- [x] Reuse the three existing models without tuning; require full 30-day outcome
      maturity before each validation month and exclude September–December.
- [x] Publish per-month errors and predictive coverage with a readable README
      figure, methods, aggregate outputs, source fingerprint and boundary tests.

The tree beats the weekday average in only one of three months. Bayesian
interval coverage remains far below the nominal 95%. This follow-up was designed
after seeing the original test, so it is not independent final validation.
It fulfils the next modelling check without adding another model or dependency.

Next: resume Milestone 4 with weather-source discovery and coverage inspection.
Use the existing weekday average as a reference; investigate changing rates and
reporting-channel composition before attributing the difficult months to weather.

## README interpretation update — 2026-10-20

- [x] Link Data Mining, Machine Learning and Bayesian Learning to implemented evidence.
- [x] Explain how to read the model chart and define predictive calibration plainly.
- [x] Connect symmetric prediction error to the Decision Analysis concept of
      asymmetric loss, explicitly leaving staffing costs and decisions unestimated.

Editorial update only: preserve the fitted models and data. Update the narrative
generator so rebuilding the README retains the explanation. Weather-source
discovery remains the next analytical step.
