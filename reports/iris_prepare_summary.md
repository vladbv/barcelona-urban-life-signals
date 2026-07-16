# IRIS preparation summary

Processed output: `data/processed/iris_2025_clean.csv`

## Row checks

| metric                           | value  |
| -------------------------------- | ------ |
| raw rows                         | 287304 |
| exact duplicate rows removed     | 3393   |
| processed rows                   | 283911 |
| repeated fitxa_id after cleaning | 0      |
| negative closure lag rows        | 0      |

## Date checks

| field             | min        | max        | missing |
| ----------------- | ---------- | ---------- | ------- |
| registration_date | 2023-10-25 | 2025-12-31 | 0       |
| closure_date      | 2025-01-01 | 2025-12-31 | 0       |

## Missingness after preparation

| column            | missing_rows | missing_percent |
| ----------------- | ------------ | --------------- |
| fitxa_id          | 0            | 0.0             |
| request_type      | 0            | 0.0             |
| area              | 0            | 0.0             |
| element           | 0            | 0.0             |
| detail            | 0            | 0.0             |
| registration_date | 0            | 0.0             |
| closure_date      | 0            | 0.0             |
| closure_lag_days  | 0            | 0.0             |
| district_code     | 88723        | 31.25           |
| district          | 88723        | 31.25           |
| neighborhood_code | 89551        | 31.54           |
| neighborhood      | 89551        | 31.54           |
| census_section    | 219213       | 77.21           |
| longitude         | 89551        | 31.54           |
| latitude          | 89551        | 31.54           |
| support           | 0            | 0.0             |
| response_channels | 0            | 0.0             |

## Rules applied

- Removed exact duplicate rows only.

- Parsed registration and closure dates from the observed day/month/year columns.

- Kept both registration and closure dates with explicit names.

- Added `closure_lag_days` for later resolution-time checks.

- Renamed selected observed columns to stable snake_case names.

## Rules not applied

- No imputation.

- No category merging.

- No removal of records with missing geography.

- No modelling features.
