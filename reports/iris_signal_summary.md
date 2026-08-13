# First IRIS signal summary

This is a first visual pass over reported citizen activity. It describes reporting patterns, not complete city conditions or causal effects.

## Quick readings

- Processed rows: 283,911

- 2025 registration rows used for headline charts: 278,628

- 2025 registration-date range: 2025-01-01 to 2025-12-31

- Median daily requests: 784

- Highest daily requests: 1,572

- Most active weekday in this export: Tuesday

- Top request area: Recollida i neteja de l'espai urbà

- Median closure lag: 3 days

- 95th percentile closure lag: 32 days

- 2025 records with district information: 68.8%

- Correlation between daily request volume and median closure lag on active days: 0.10

## Figures

- `reports/figures/iris_daily_registration_volume.png`
- `reports/figures/iris_weekday_pattern.png`
- `reports/figures/iris_top_request_areas.png`
- `reports/figures/iris_district_distribution.png`
- `reports/figures/iris_closure_lag_histogram.png`
- `reports/figures/iris_daily_volume_vs_closure_lag.png`
- `reports/figures/iris_month_weekday_heatmap.png`
- `reports/figures/iris_area_volume_vs_lag.png`
- `reports/figures/iris_district_area_mix_heatmap.png`
- `reports/figures/iris_support_mix_by_area.png`

## Notes

- The headline charts focus on records registered in 2025, because the source export is closure-year oriented and contains a small number of older registrations.

- District charts include missing geography explicitly instead of hiding it.

- Category language variants are not normalised yet, so request type comparisons should wait until that decision is documented.

- Scatter plots show association surfaces for follow-up questions; they are not causal estimates.

- Channel-mix charts are reporting-behaviour signals. They may reflect access, habits, and municipal workflow, not only the underlying urban issue.
