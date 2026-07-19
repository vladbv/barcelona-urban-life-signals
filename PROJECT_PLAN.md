# Project plan

## Goal

Explore how citizen-reported city signals in Barcelona relate to recurring
calendar patterns, weather, place, and city activity. Later phases may use
regression, anomaly detection, and forecasting where the data supports them.

## Milestone 1 — Discover and understand IRIS

Status: complete

- [x] Create a reproducible local Python environment.
- [x] Add commands to list current Open Data BCN IRIS resources.
- [x] Add a format-agnostic CSV inspection command.
- [x] Review the catalog output and select the appropriate IRIS resource.
- [x] Download the source into `data/raw/`.
- [x] Inspect columns, data types, missingness, duplicate rows, and sample data.
- [x] Add a focused IRIS profiling command for date coverage, duplicates,
      geography missingness, and main classification distributions.
- [x] Identify observed registration and closure date coverage.
- [x] Record the selected resource ID, download date, and catalog metadata.
- [x] Inspect duplicate `FITXA_ID` rows and document the initial handling rule.
- [x] Investigate why some 2025 closure records have older registration dates.

Initial Milestone 1 conclusions:

- The selected resource is `2025_IRIS_Peticions_Ciutadanes_OpenData.csv`
  (`efc9fd4d-a812-427c-846d-a086d22012a4`).
- The 2025 export appears to be closure-year oriented: closure dates are within
  2025, while 5,284 rows were registered before 2025.
- Duplicate `FITXA_ID` values currently appear to be exact duplicate rows:
  after exact de-duplication, no repeated `FITXA_ID` values remain.
- Geography is not complete enough to treat all requests as place-specific:
  district is missing for 31.27% of rows and census section for 77.24%.

Exit criterion: we can describe the real schema and limitations of the selected
IRIS file without relying on guessed field names.

## Milestone 2 — Prepare an analysis dataset

- [x] Remove exact duplicate rows as a reproducible rule.
- [x] Keep both registration and closure dates, with explicit naming.
- [x] Use registration date for reported-demand rhythm unless the analysis question
  is about resolution timing.
- [x] Define cleaning rules from the observed schema.
- [x] Parse and validate relevant dates.
- [x] Standardise only fields needed for the first analysis.
- [x] Save reproducible outputs under `data/processed/`.
- [x] Add basic checks for row counts, nulls, and transformation assumptions.
- [ ] Decide whether category language variants should be normalised, for
      example `INCIDENCIA` and `ISSUE`.
- [x] Create the first exploratory charts from the processed dataset.

Initial Milestone 2 output:

- `data/processed/iris_2025_clean.csv` is generated locally and ignored by Git.
- `reports/iris_prepare_summary.md` records the preparation checks.
- `reports/iris_signal_summary.md` records first visible signal readings.
- `reports/figures/` contains generated charts for daily volume, weekday
  rhythm, request areas, and district/missing-geography distribution.
- `streamlit_app.py` provides the first local interface over the processed
  dataset.

## Milestone 3 — Explore urban patterns

- [x] Establish first request-volume trends and weekday rhythm.
- [ ] Compare meaningful geographic or request groupings supported by the data.
- [ ] Examine civic behaviour carefully, including possible reporting bias.
- [x] Produce clear static charts and document findings and caveats.
- [x] Add a first local interface for filtering and reading the processed data.

## Milestone 4 — Add weather context

- Select a reliable Barcelona weather source and align its time resolution.
- Test relationships with transparent summaries and regression baselines.
- Distinguish association from causal claims.
- After weather and seasonality baselines exist, add dated policy/event context
  from Barcelona, Catalunya, and Spain as documented external variables.

## Later, only after the evidence supports it

- anomaly detection;
- time-aware predictive baselines and model evaluation;
- city-activity or event data;
- richer application polish and deployment.

Advanced modelling is not a prerequisite. Each later addition must answer a
specific question better than a simpler analysis.
