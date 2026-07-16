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
| Catalog checked | 2026-07-16 |

Download URL observed from the live catalog:

```text
https://opendata-ajuntament.barcelona.cat/data/dataset/15b349cd-3d4d-4a62-9ad3-d67230029a23/resource/efc9fd4d-a812-427c-846d-a086d22012a4/download
```

## Why this resource

The 2025 CSV is a stable annual CSV export and is small enough to inspect
locally. It gives enough volume for date, geography, request-type, and channel
checks before introducing weather or other context.

## Catalog context

The live catalog also exposes CSV and XML resources for multiple years,
including 2026, 2025, 2024, 2023, and older annual files. The current milestone
continues with the 2025 CSV only so the schema and limitations can be understood
before combining years.
