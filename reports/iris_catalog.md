# IRIS catalog selection

This project currently uses one Open Data BCN IRIS resource as the first source
for data understanding.

## Selected resource

| field | value |
| --- | --- |
| Dataset | IRIS |
| Resource name | `2025_IRIS_Peticions_Ciutadanes_OpenData.csv` |
| Resource ID | `efc9fd4d-a812-427c-846d-a086d22012a4` |
| Format | CSV |
| Local raw path | `data/raw/2025_IRIS_Peticions_Ciutadanes_OpenData.csv` |
| Local file timestamp | 2026-07-09 11:50:24 +0300 |
| Catalog checked | 2026-09-27 |

Download URL observed from the live catalog:

```text
https://opendata-ajuntament.barcelona.cat/data/dataset/15b349cd-3d4d-4a62-9ad3-d67230029a23/resource/efc9fd4d-a812-427c-846d-a086d22012a4/download
```

## Why this resource

The 2025 CSV is an annual CSV export and is small enough to inspect
locally. It gives enough volume for date, geography, request-type, and channel
checks before introducing weather or other context.

## Catalog context

The live catalog also exposes CSV and XML resources for multiple years,
including 2026, 2025, 2024, 2023, and older annual files. The current milestone
continues with the 2025 CSV only so the schema and limitations can be understood
before combining years.

## Snapshot verification (2026-09-27)

The live catalog was queried again using `python -m src.data_catalog`; the
2025 resource ID, name and download URL above remain listed. The existing raw
download was retained. This verifies resource availability, not byte-for-byte
equality with the current remote download or completeness of 2025 registrations.

Local raw SHA-256:
`55e017aae02eec8a0864b6189fe6dcf24664dd2bbb200aea1078594e25380332`.

The processed dataset was reproduced in memory from this raw snapshot and
matched the existing CSV, allowing for CSV numeric dtype round-tripping.
Regenerated analysis rules and fingerprints are recorded in
`iris_analysis_manifest.json`.


## Adjacent snapshot (2026-10-02)

The full catalog response is preserved locally as
`data/raw/iris_catalog_2026-10-02.json`. The selected later CSV resource is
`eae9a19a-4543-45db-bc13-3e3073b58324`, downloaded to
`data/raw/2026_IRIS_Peticions_Ciutadanes_OpenData_2026-10-02.csv` (15,406,383 bytes).
Its observed closures span 2026-01-01 to 2026-03-31. Download date and observed
data coverage are distinct; catalog metadata supplies no completeness guarantee.

SHA-256: `e5ae6711791186136998bb19198ce6cae4fd53da18d9a2146a43e10630e5a388`.
Source inspection and the comparison are documented in
[iris_2026_profile.md](iris_2026_profile.md) and
[iris_observation_windows.md](iris_observation_windows.md).
