# Project instructions

## Purpose

Barcelona Urban Life Signals explores relationships between citizen requests,
seasonality, weather pressure, civic behaviour, and activity in Barcelona.

## Current scope

Work only on data discovery and understanding until the IRIS source has been
downloaded and inspected.

- Discover resources from the live Open Data BCN catalog.
- Keep original downloads in `data/raw/`.
- Inspect and document the actual schema before writing transformations.
- Keep generated or cleaned data in `data/processed/`.
- Prefer small, reproducible Python modules and clear commands.

Do not add dashboards, event analysis, advanced forecasting, Bayesian models,
or speculative feature engineering during this milestone.

## Engineering guidelines

- Use Python 3.11 and the dependencies in `requirements.txt`.
- Do not invent, rename, or rely on dataset columns before inspecting the CSV.
- Never modify raw data in place.
- Keep paths relative to the project root and avoid machine-specific settings.
- Add dependencies only when the current milestone needs them.
- Keep notebooks for exploration; put reusable logic in `src/`.
- Update the README and project plan when commands or scope change.
- Validate changes with relevant CLI help, syntax, and lightweight runtime
  checks.

## Communication

Explain assumptions and data limitations plainly. Describe IRIS as reported
citizen activity, not complete ground truth or proof of causation.
