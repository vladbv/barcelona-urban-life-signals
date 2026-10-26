# Reproduce Barcelona Urban Life Signals

Use Python 3.11 and the existing dependencies:

```bash
python3.11 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
```

For the data already present in this workspace, regenerate the IRIS reports and README highlights:

```bash
python -m src.explore_iris_signals --readme-path README.md
python -m streamlit run streamlit_app.py
```

The analysis command validates the prepared schema, IDs, dates and closure
lags, then writes:

- three selected findings in `README.md`, with compact charts;
- `reports/iris_signal_summary.md` — all 13 original plot readings with supporting tables;
- `reports/iris_exploration.html` — a standalone report with embedded plots and CSVs;
- `reports/figures/` — 13 detailed plots and, with `--readme-path`, three compact README charts;
- `data/processed/summaries/` — 13 aggregate CSVs, ignored by Git;
- `reports/iris_analysis_manifest.json` — input fingerprints, versions, and rules.

The README uses relative Markdown image paths, so GitHub can display every
plot directly when the README and PNGs are committed together. No running app,
external image host, or notebook execution is needed to read the plots.
Raw data, processed record-level data, and regenerated aggregate CSVs stay out
of Git. Aggregate tables are also embedded in the standalone report.

Full plot interpretations live in `src/iris_interpretations.py`; the short README readings and compact charts live in `src/iris_highlights.py`. The command
above recomputes the quoted numbers and updates only the marked plot section
of the README, preserving the introduction and setup instructions. Omit
`--readme-path` to regenerate the reports without editing the README.
The prose describes this inspected snapshot; review its interpretation when
changing source data.

To work from a fresh checkout, first discover and inspect the source:

```bash
python -m src.data_catalog
python -m src.data_catalog --download efc9fd4d-a812-427c-846d-a086d22012a4
python -m src.inspect_data data/raw/2025_IRIS_Peticions_Ciutadanes_OpenData.csv
python -m src.profile_iris data/raw/2025_IRIS_Peticions_Ciutadanes_OpenData.csv
python -m src.investigate_iris_quality data/raw/2025_IRIS_Peticions_Ciutadanes_OpenData.csv
python -m src.prepare_iris_dataset data/raw/2025_IRIS_Peticions_Ciutadanes_OpenData.csv
python -m src.explore_iris_signals --readme-path README.md
```

The download command refuses to overwrite an existing raw file. Catalog
metadata and download provenance are in [iris_catalog.md](reports/iris_catalog.md).
If the portal is unavailable, preserve an original CSV downloaded from the
[IRIS dataset page](https://opendata-ajuntament.barcelona.cat/data/en/dataset/iris)
in `data/raw/`, then inspect it before preparing data. A fresh remote download
may differ from this preserved snapshot; regenerate and inspect the outputs.

Output paths are configurable with `python -m src.explore_iris_signals --help`.
The current analysis explicitly expects the inspected **2025 closure-year**
schema and rejects inconsistent dates or duplicate identifiers.

Run the lightweight analytical and interface checks:

```bash
python -m unittest discover -s tests -v
python -m compileall -q src streamlit_app.py
```

## Project structure

```text
data/raw/                 Original downloads, never edited in place
data/processed/           Prepared records, summaries, and local caches
reports/figures/           Exported scientific/descriptive plots
reports/*.md              Profiles, decisions, and generated reading guide
reports/*.html            Standalone illustrated report
reports/*.json            Reproducibility manifest
src/iris_signals.py        Shared cohort, calendar, and composition calculations
src/explore_iris_signals.py CLI and static plots
src/iris_interpretations.py Per-plot narratives shared across all reading formats
src/iris_report.py         Markdown, offline HTML, and README narrative generation
src/*                     Discovery, inspection, quality, and preparation
streamlit_app.py           Existing local explorer over the same calculations
tests/                    Calendar, denominator, input, and interface regressions
```

## Reproduce the follow-up audit

For the dated files already present locally:

```bash
python -m src.audit_iris_observation
```

On a fresh checkout, preserve the catalog and later export before inspecting it:

```bash
python -m src.data_catalog --catalog-output data/raw/iris_catalog_2026-10-02.json --download eae9a19a-4543-45db-bc13-3e3073b58324 --download-path data/raw/2026_IRIS_Peticions_Ciutadanes_OpenData_2026-10-02.csv
python -m src.inspect_data data/raw/2026_IRIS_Peticions_Ciutadanes_OpenData_2026-10-02.csv
python -m src.profile_iris data/raw/2026_IRIS_Peticions_Ciutadanes_OpenData_2026-10-02.csv --report-path reports/iris_2026_profile.md --daily-output-path data/processed/iris_2026_daily_raw.csv
python -m src.audit_iris_observation
```

The snapshot names above identify the inspected inputs, not a historical
version supplied by the server. A download made later may have different
contents; use its actual date in new filenames, pass them with `--later-raw`
and `--catalog`, and inspect it before rerunning the audit. Downloads refuse
to overwrite existing files and install only complete responses.

The audit writes its four CSVs, including the combined observed records under
`data/processed/observation_audit/`, plus a Markdown report, source fingerprints,
and the comparison plot. It does not replace the original explorer's dataset.

## Next according to the plan

The observation-window audit is complete for the two preserved snapshots.
Request-type translations remain unverified: the catalog defines the field
but provides no mapping of its values. Two new area labels and many new detail
labels also mean that category comparisons need care.

The official 2025 weather source is now inspected (see the command below).
Next, verify day boundaries and quality provenance for the narrow question:
are daily weather conditions associated with the number of observed cleaning
requests that close within 30 days? Check a 90-day definition and weekday/month
differences. The cleaning area's published name is shared by both exports;
that alone does not prove that classification practice was unchanged.
No weather data has been joined and no weather effect is established yet.
See [PROJECT_PLAN.md](PROJECT_PLAN.md) for the remaining work.

## Reproduce the neighbourhood comparison

```bash
python -m src.neighbourhood_quadrants --download
```

This downloads missing official source files only; the historical survey CSV is
approximately 570 MB. Omit `--download` for an offline rebuild. Rent and resident
satisfaction are separate from IRIS. See [sources, methods and all 73 neighbourhoods](reports/neighbourhood_living.md).

## Reproduce the Bayesian and machine-learning comparison

After preparing and auditing the two inspected exports above:

```bash
python -m src.model_iris_counts --help
python -m src.model_iris_counts --readme-path README.md
python -m unittest discover -s tests -v
```

The model command uses `data/processed/observation_audit/iris_observed_2025_records.csv`
and downloads nothing. It writes aggregate training counts, predictions, metrics,
posterior summaries and diagnostics to `data/processed/models/`, plus two plots,
`reports/iris_model_comparison.md` and `reports/iris_model_manifest.json`.
The README findings are regenerated inside their own marker pair; the original
descriptive charts retain their separate 2025 closure-year population.

The fixed October 1 prediction origin excludes training dates whose full 30-day
or 90-day closure window has not ended. Features use calendar dates only. The
settings, input fingerprint, package versions and simulation seed are recorded.
No dependency beyond `requirements.txt` is needed. Historical publication delays
remain unknown. Treat October–December as an already-inspected test period in
future development; do not tune models against these published results.

## Check stability across earlier months

```bash
python -m src.validate_iris_models --readme-path README.md
```

This reuses the audited input and fixed model settings. It refits before April,
June and August, using only earlier dates with fully matured 30-day outcomes.
September–December data do not enter these fits or scores. The validation design
was added after the original test was seen; it is a retrospective diagnostic,
not a fresh final test or a hyperparameter search.

Outputs: `data/processed/models/iris_validation_*.csv`,
`reports/iris_temporal_validation.md`, `reports/iris_validation_manifest.json`
and one figure. The optional README update uses a separate marker pair and
preserves the existing findings. No new download or dependency is needed.

The same command also exports `iris_validation_error_direction.csv` and
`reports/figures/iris_error_direction.png`. Signed errors are observed minus
predicted counts, calculated before rounding. The report and manifest include
mean signed error, MAE and counts of underpredicted, overpredicted and exact days.
This diagnostic uses the existing validation predictions without retuning models.

## Inspect the weather source and joins

```bash
python -m src.audit_weather --download --snapshot 2026-10-26 --readme-path README.md
```

This preserves missing official catalogs and CSVs in `data/raw/` and refuses to
overwrite them. The catalog resource names select the 2025 observations,
variable definitions and 2020 station metadata. These are live resources, not
server-versioned historical files: use the actual retrieval date as `--snapshot`
for a new download and inspect its resulting coverage before further analysis.
Omit `--download` when rebuilding preserved files offline.

The command generates two CSVs under `data/processed/weather/`, a coverage plot,
`reports/weather_source_audit.md` and `reports/weather_manifest.json`. The README
update has its own marker pair. It checks unique observation keys, station
identity consistency and many-to-one metadata joins. Missing weather stays
missing; no station value is assigned to an IRIS neighbourhood.

No new dependency is needed. Before a weather/IRIS join, verify the weather
daily aggregation boundaries and measurement quality; record presence alone
does not establish either. See the source report for provisional station choice.
