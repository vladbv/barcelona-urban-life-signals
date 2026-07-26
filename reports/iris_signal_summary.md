# First IRIS signal summary

This is a first visual pass over reported citizen activity. It describes reporting patterns, not complete city conditions or causal effects.

## Quick readings

- Processed rows: 283,911

- Registration-date range: 2023-10-25 to 2025-12-31

- Median daily requests: 496

- Highest daily requests: 1,572

- Most active weekday in this export: Tuesday

- Top request area: Recollida i neteja de l'espai urbà

- Median closure lag: 4 days

- 95th percentile closure lag: 34 days

- Correlation between daily request volume and median closure lag on active days: -0.53

## Figures

- `reports/figures/iris_daily_registration_volume.png`
- `reports/figures/iris_weekday_pattern.png`
- `reports/figures/iris_top_request_areas.png`
- `reports/figures/iris_district_distribution.png`
- `reports/figures/iris_closure_lag_histogram.png`
- `reports/figures/iris_daily_volume_vs_closure_lag.png`
- `reports/figures/iris_month_weekday_heatmap.png`
- `reports/figures/iris_area_volume_vs_lag.png`

## Notes

- Because the 2025 file is closure-year oriented, registration dates before 2025 are visible in the early part of the daily chart.

- District charts include missing geography explicitly instead of hiding it.

- Category language variants are not normalised yet, so request type comparisons should wait until that decision is documented.

- Scatter plots show association surfaces for follow-up questions; they are not causal estimates.
