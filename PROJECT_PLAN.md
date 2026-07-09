# Project plan

## Goal

Explore how citizen-reported city signals in Barcelona relate to recurring
calendar patterns, weather, place, and city activity. Later phases may use
regression, anomaly detection, and forecasting where the data supports them.

## Milestone 1 — Discover and understand IRIS

Status: in progress

- [x] Create a reproducible local Python environment.
- [x] Add commands to list current Open Data BCN IRIS resources.
- [x] Add a format-agnostic CSV inspection command.
- [ ] Review the catalog output and select the appropriate IRIS resource.
- [ ] Download the source into `data/raw/`.
- [ ] Inspect columns, data types, missingness, duplicate rows, and sample data.
- [ ] Identify date coverage and update frequency from observed data/metadata.
- [ ] Record the selected resource, download date, and initial data-quality notes.

Exit criterion: we can describe the real schema and limitations of the selected
IRIS file without relying on guessed field names.

## Milestone 2 — Prepare an analysis dataset

- Define cleaning rules from the observed schema.
- Parse and validate relevant dates.
- Standardise only fields needed for the first analysis.
- Save reproducible outputs under `data/processed/`.
- Add basic checks for row counts, nulls, and transformation assumptions.

## Milestone 3 — Explore urban patterns

- Establish request-volume trends and calendar seasonality.
- Compare meaningful geographic or request groupings supported by the data.
- Examine civic behaviour carefully, including possible reporting bias.
- Produce clear static charts and document findings and caveats.

## Milestone 4 — Add weather context

- Select a reliable Barcelona weather source and align its time resolution.
- Test relationships with transparent summaries and regression baselines.
- Distinguish association from causal claims.

## Later, only after the evidence supports it

- anomaly detection;
- time-aware predictive baselines and model evaluation;
- city-activity or event data;
- a small Streamlit application.

Advanced modelling is not a prerequisite. Each later addition must answer a
specific question better than a simpler analysis.
