<p align="center">
  <img src="assets/barcelona-title.svg" alt="Barcelona Urban Life Signals" width="100%">
</p>

![A warm Barcelona apartment overlooking city life, with subtle data patterns in the interior](assets/barcelona-urban-life-signals-hero.png)

<p align="center"><em>Fem un vermut?</em></p>

Barcelona changes with the weather, the calendar, and the way people use the
city. This project explores whether those changes are visible in public data:
the seasonal patterns, unusual moments, neighbourhood differences, and civic
behaviours that appear when thousands of individual reports are viewed
together.

The starting point is Barcelona City Council's IRIS dataset: citizen incidents,
complaints, suggestions, inquiries, and messages of gratitude. I want to use
these records as signals of urban life and ask:

- Which types of requests have recurring weekly or seasonal patterns?
- How do patterns differ across parts of Barcelona?
- Are changes in weather associated with changes in reported city pressure?
- Which movements look unusual rather than seasonal?
- What can the data tell us about civic behaviour, and where are its limits?

The aim is to find useful relationships, not to imply that correlation proves
cause. IRIS measures what people report to the council. It does not measure
every issue in the city, and reporting behaviour may vary between communities,
channels, and periods.

## Where the project is now

The first dataset is now in place: 287,304 IRIS records from the 2025 resource
published by Open Data BCN. The initial inspection found 25 columns, substantial
missingness in geographic fields, and 3,393 exact duplicate rows.

The first data-quality pass is documented in `reports/`. The 2025 export looks
closure-year oriented: all closure dates are in 2025, while some requests were
registered before 2025. Repeated `FITXA_ID` values currently disappear after
exact de-duplication, so the first processed dataset removes exact duplicate
rows only and keeps the missing geography visible.

The current work is to prepare a careful first analysis dataset:

- preserve registration and closure dates separately;
- keep reported-demand analysis based on registration date;
- avoid imputing missing geography;
- document any category normalisation before applying it.

Weather integration, regression, seasonal analysis, anomaly detection, and an
application come after this data-quality work.

## Setup

Python 3.11 is recommended.

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

Check that the environment and project imports work:

```bash
python -m src.data_catalog --help
python -m src.inspect_data --help
```

## First data commands

List the live IRIS resources published by Open Data BCN:

```bash
python -m src.data_catalog
```

Each resource is printed with its ID, format, description, and source URL.
Review that list before downloading anything. Then download one resource by its
ID:

```bash
python -m src.data_catalog --download RESOURCE_ID
```

Downloads are saved under `data/raw/`. Raw files are never modified in place.
Inspect the downloaded CSV without assuming any column names:

```bash
python -m src.inspect_data data/raw/FILENAME.csv
```

Create the first focused IRIS profile after the raw schema is known:

```bash
python -m src.profile_iris data/raw/FILENAME.csv
```

This writes a Markdown profile to `reports/iris_profile.md` and a reproducible
daily request-count file to `data/processed/iris_daily_requests.csv`. The daily
file is generated output and is not committed.

Investigate the first data-quality questions:

```bash
python -m src.investigate_iris_quality data/raw/FILENAME.csv
```

This writes `reports/iris_quality_notes.md`, including duplicate `FITXA_ID`
checks and registration-versus-closure timing.

Prepare the first conservative analysis dataset:

```bash
python -m src.prepare_iris_dataset data/raw/FILENAME.csv
```

This writes `data/processed/iris_2025_clean.csv` and
`reports/iris_prepare_summary.md`. The processed CSV is generated output and is
not committed.

Create the first visual signal outputs:

```bash
python -m src.explore_iris_signals
```

This writes `reports/iris_signal_summary.md` and generated PNG charts under
`reports/figures/`. The figures are reproducible output and are not committed.

Current tracked notes:

- `reports/iris_catalog.md` records the selected Open Data BCN resource.
- `reports/iris_profile.md` records the first schema and distribution profile.
- `reports/iris_quality_notes.md` records duplicate and timing checks.
- `reports/iris_prepare_summary.md` records the first preparation checks.
- `reports/iris_signal_summary.md` records the first visual signal readings.

If the portal is unavailable, open the
[IRIS dataset page](https://opendata-ajuntament.barcelona.cat/data/en/dataset/iris)
and place a downloaded CSV in `data/raw/`, then run the same inspection command.

## Project structure

```text
.
├── data/
│   ├── raw/          # original downloads; ignored by Git
│   └── processed/    # reproducible analysis-ready outputs; ignored by Git
├── notebooks/        # exploratory notebooks, added when the schema is known
├── reports/
│   ├── figures/      # exported charts
│   └── *.md          # tracked data-understanding notes
├── src/
│   ├── data_catalog.py
│   ├── explore_iris_signals.py
│   ├── investigate_iris_quality.py
│   ├── inspect_data.py
│   ├── prepare_iris_dataset.py
│   └── profile_iris.py
├── AGENTS.md
├── PROJECT_PLAN.md
├── README.md
└── requirements.txt
```

## Stack

The initial stack is intentionally ordinary: Python, pandas, NumPy,
matplotlib, scikit-learn, and Jupyter. These tools cover data inspection,
analysis, visualisation, and later baseline modelling without adding
infrastructure early.

Streamlit is a possible presentation layer later, once there is a stable
processed dataset and a clear set of findings. It is not part of the current
environment.

See [PROJECT_PLAN.md](PROJECT_PLAN.md) for the phased scope.
