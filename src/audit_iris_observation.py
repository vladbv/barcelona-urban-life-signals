"""Audit later closures and equal follow-up periods without changing the original cohort."""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

import pandas as pd

from src.prepare_iris_dataset import prepare_dataset
from src.profile_iris import markdown_table
from src.iris_signals import read_prepared

BASE = Path('data/processed/iris_2025_clean.csv')
LATER = Path('data/raw/2026_IRIS_Peticions_Ciutadanes_OpenData_2026-10-02.csv')
CATALOG = Path('data/raw/iris_catalog_2026-10-02.json')


def validate_source(frame: pd.DataFrame, closure_year: int) -> None:
    if frame.empty or frame.fitxa_id.isna().any() or frame.fitxa_id.duplicated().any():
        raise ValueError('Each source must have unique, nonmissing IDs after exact deduplication.')
    if frame[['registration_date', 'closure_date']].isna().any().any():
        raise ValueError('Invalid dates in the source.')
    lag = (frame.closure_date - frame.registration_date).dt.days
    if lag.lt(0).any() or not lag.eq(frame.closure_lag_days).all():
        raise ValueError('Invalid closure lag in the source.')
    if not frame.closure_date.dt.year.eq(closure_year).all():
        raise ValueError(f'Expected closure dates within {closure_year}.')


def compare_sources(base: pd.DataFrame, later: pd.DataFrame, year: int = 2025):
    validate_source(base, year)
    validate_source(later, year + 1)
    overlap = set(base.fitxa_id) & set(later.fitxa_id)
    if overlap:
        raise ValueError(f'{len(overlap)} IDs occur in both exports; investigate before combining.')
    cutoff = later.closure_date.max()
    first = base.loc[base.registration_date.dt.year.eq(year)].copy()
    added = later.loc[later.registration_date.dt.year.eq(year)].copy()
    first['closure_export_year'] = year
    added['closure_export_year'] = year + 1
    cohort = pd.concat([first, added], ignore_index=True).sort_values(['registration_date', 'fitxa_id'])
    calendar = pd.date_range(f'{year}-01-01', f'{year}-12-31', name='registration_date')
    daily = pd.DataFrame(index=calendar)
    daily['original_records'] = first.groupby('registration_date').size().reindex(calendar, fill_value=0)
    daily['later_closure_records'] = added.groupby('registration_date').size().reindex(calendar, fill_value=0)
    daily['observed_combined_records'] = daily.original_records + daily.later_closure_records
    for days in (30, 90):
        eligible = calendar + pd.Timedelta(days=days) <= cutoff
        counts = cohort.loc[cohort.closure_lag_days.le(days)].groupby('registration_date').size().reindex(calendar, fill_value=0)
        daily[f'eligible_{days}d'] = eligible
        daily[f'closed_within_{days}d'] = counts.where(eligible).astype('Int64')
    monthly = daily.groupby(daily.index.to_period('M').astype(str)).agg(
        original_records=('original_records', 'sum'),
        later_closure_records=('later_closure_records', 'sum'),
        observed_combined_records=('observed_combined_records', 'sum'),
    )
    monthly.index.name = 'registration_month'
    monthly['increase_percent'] = monthly.later_closure_records.div(monthly.original_records.replace(0, float('nan'))) * 100
    # A partial observation window must not silently become a full-month count.
    for days in (30, 90):
        groups = daily.groupby(daily.index.to_period('M').astype(str))
        complete = groups[f'eligible_{days}d'].all()
        monthly[f'closed_within_{days}d'] = groups[f'closed_within_{days}d'].sum(min_count=1).where(complete).astype('Int64')
    label_rows = []
    for column in ('request_type', 'area', 'element', 'detail'):
        known = set(base[column].dropna())
        for label, count in later[column].value_counts(dropna=False).items():
            label_rows.append({'field': column, 'published_label': label, 'later_records': int(count), 'seen_in_2025_export': label in known})
    return cohort, daily.reset_index(), monthly.reset_index(), pd.DataFrame(label_rows), cutoff


def save_figure(monthly: pd.DataFrame, path: Path, cutoff: pd.Timestamp) -> None:
    from src.explore_iris_signals import plt, BARCELONA, style_axis
    import numpy as np
    x = np.arange(len(monthly))
    fig, axes = plt.subplots(2, 1, figsize=(12, 8), sharex=True)
    axes[0].bar(x, monthly.original_records, color=BARCELONA['sea'], label='Closed in 2025: original view')
    axes[0].bar(x, monthly.later_closure_records, bottom=monthly.original_records, color=BARCELONA['tile'], label='Additional closures in the 2026 snapshot')
    style_axis(axes[0], 'Later closures add reports to the end-of-year picture', ylabel='Observed requests registered that month')
    axes[0].legend(frameon=False)
    axes[1].bar(x, monthly.increase_percent, color=BARCELONA['terracotta'])
    style_axis(axes[1], '', 'Registration month in 2025', 'Increase over the original count (%)')
    axes[1].set_xticks(x, [pd.Timestamp(m).strftime('%b') for m in monthly.registration_month])
    fig.set_facecolor(BARCELONA['paper'])
    fig.text(.02, .02, f'Original and later closure exports; registration year 2025. Later closures observed through {cutoff.date()}.\nStill-open requests and closures outside these snapshots remain unknown. This is not a complete demand count.', fontsize=9)
    fig.tight_layout(rect=(0, .08, 1, 1))
    path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(path, dpi=150)
    plt.close(fig)


def fingerprint(path: Path) -> dict:
    with path.open('rb') as stream:
        return {'path': str(path), 'sha256': hashlib.file_digest(stream, 'sha256').hexdigest()}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--base', type=Path, default=BASE)
    parser.add_argument('--base-raw', type=Path, default=Path('data/raw/2025_IRIS_Peticions_Ciutadanes_OpenData.csv'))
    parser.add_argument('--later-raw', type=Path, default=LATER)
    parser.add_argument('--catalog', type=Path, default=CATALOG)
    args = parser.parse_args()
    base = read_prepared(args.base)
    raw = pd.read_csv(args.later_raw, low_memory=False)
    if list(raw.columns) != list(pd.read_csv(args.base_raw, nrows=0).columns):
        raise ValueError('Raw source schemas differ; inspect and document before combining.')
    later = prepare_dataset(raw)
    cohort, daily, monthly, labels, cutoff = compare_sources(base, later)
    output = Path('data/processed/observation_audit')
    output.mkdir(parents=True, exist_ok=True)
    for name, table in [('observed_2025_records', cohort), ('daily', daily), ('monthly', monthly), ('published_labels', labels)]:
        table.to_csv(output / f'iris_{name}.csv', index=False)
    figure = Path('reports/figures/iris_later_closures.png')
    save_figure(monthly, figure, cutoff)
    catalog = json.loads(args.catalog.read_text())['result']
    publisher_type = next(item['value'] for item in catalog['extras'] if item['key'] == '02.TIPUS')
    stability = labels.groupby('field').apply(
        lambda g: pd.Series({'later_unique_labels': len(g), 'new_labels': int((~g.seen_in_2025_export).sum()),
                            'later_records_with_new_label': int(g.loc[~g.seen_in_2025_export, 'later_records'].sum())}),
        include_groups=False,
    ).reset_index()
    december = monthly.iloc[-1]
    added_count = int(monthly.later_closure_records.sum())
    source_summary = pd.DataFrame([
        {'source': '2025 preserved export', 'deduplicated_rows': len(base), 'first_closure': str(base.closure_date.min().date()), 'last_closure': str(base.closure_date.max().date())},
        {'source': '2026 dated snapshot', 'deduplicated_rows': len(later), 'first_closure': str(later.closure_date.min().date()), 'last_closure': str(cutoff.date())},
    ])
    manifest = {
        'sources': [fingerprint(args.base_raw), fingerprint(args.base), fingerprint(args.later_raw), fingerprint(args.catalog)],
        'later_resource_id': 'eae9a19a-4543-45db-bc13-3e3073b58324',
        'source_url': 'https://opendata-ajuntament.barcelona.cat/data/en/dataset/iris',
        'observed_last_closure': str(cutoff.date()), 'later_raw_rows': len(raw),
        'later_exact_duplicates_removed': len(raw) - len(later), 'later_columns': list(raw.columns),
        'cross_export_id_overlap': 0, 'added_2025_registrations': added_count,
        'combined_observed_2025_registrations': len(cohort),
        'followup_days': [30, 90], 'followup_endpoint': 'registration_date + horizon <= observed_last_closure; inclusive lag <= horizon',
        'coverage_warning': 'Observed date maxima do not certify publisher completeness. Still-open and unpublished records are unknown.',
        'category_policy': 'No label merging; publisher field definition does not provide a value crosswalk.',
    }
    report = [
        '# What later closures change about the 2025 picture',
        f'**Takeaway: the 2026 snapshot adds {added_count:,} requests registered in 2025. December gains {int(december.later_closure_records):,} records ({december.increase_percent:.1f}% above its original count).**',
        'The new file was downloaded on 2026-10-02, but its latest recorded closure is '
        f'**{cutoff.date()}**. A recent download is not necessarily up-to-date coverage.',
        '![Original monthly counts plus requests closed in the later snapshot](figures/iris_later_closures.png)',
        'Read the blue bars as the original monthly counts and the gold segments as reports recovered from later closures. '
        'The lower panel shows the percentage added to each original count. December changes most: '
        f'its count rises from {int(december.original_records):,} to {int(december.observed_combined_records):,}. '
        'This demonstrates that the year-end selection changes the picture. It does not explain every monthly rise or fall.',
        'A request can remain important to someone after New Year. Following it into the next export helps keep those longer administrative processes visible. '
        'Neither this combined count nor the original count includes every request that might still be open.',
        '## Source and identity checks', markdown_table(source_summary),
        f'The inspected 2026 file has {len(raw):,} raw rows and {len(raw.columns)} columns; '
        f'{len(raw) - len(later):,} exact duplicates were removed. The observed column names match the 2025 schema. '
        'IDs are unique after exact deduplication in each source, with no IDs shared between these snapshots. '
        'Dates and nonnegative closure lags were validated before combining. The original 2025 dataset and its 13-plot tour are preserved.',
        '## Monthly comparison', markdown_table(monthly.round(2)),
        'The percentages above use the original monthly count as denominator. They are increases in observed records, not estimates of missingness among all citizen requests.',
        '## An equal amount of follow-up time',
        '**Primary descriptive outcome:** the daily number of observed requests registered in 2025 and administratively closed within 30 calendar days. '
        '**Sensitivity outcome:** the same count allowing 90 days. Include lag zero and the endpoint (30 or 90). '
        'Only include a registration date when that date plus the full period is on or before the last observed closure date.',
        f'All {int(daily.eligible_30d.sum())} calendar days in 2025 satisfy the 30-day date rule; '
        f'{int(daily.eligible_90d.sum())} satisfy the 90-day rule. In these snapshots, '
        f'{int(daily.closed_within_30d.sum()):,} records meet the 30-day definition and '
        f'{int(daily.closed_within_90d.sum()):,} meet the 90-day definition. '
        'A December 31 registration has its 30-day endpoint on January 30 and its 90-day endpoint on March 31.',
        '**What this makes comparable:** every included registration date gets the same allowed time to contribute a closed record. '
        '**What it does not fix:** unknown unpublished or still-open requests, changes in reporting, and differences in administrative processing. '
        'These counts describe requests that close within a fixed period; they are not total demand, a closure success rate, or the waiting time of all requests. '
        'The maximum observed date is a practical date boundary, not publisher certification of complete coverage.',
        '## Classification stability and publisher documentation', markdown_table(stability),
        'Exact source strings are compared without translation, accent removal, or merging. '
        'A new label may reflect spelling, classification, or a new kind of request; the table does not determine which.',
        f'The live catalog defines TIPUS as “{publisher_type}”. This describes the field but supplies no mapping between its values. '
        'The 2026 snapshot uses INCIDÈNCIA, whereas the older export includes INCIDENCIA and ISSUE. '
        'A crosswalk is therefore still unverified. Do not compare or merge these labels as though equivalence had been established. '
        'The complete label audit, including area, element, and detail differences, is exported as iris_published_labels.csv.',
        '## Next weather question and boundaries',
        'Start with cleaning and collection, whose published AREA label appears in both exports. A shared name does not establish unchanged classification practices. '
        'Ask whether daily weather is associated with counts of those observed requests closed within 30 days, '
        'checking a 90-day definition and weekday/month differences. This concerns a selected group of reports, not all urban problems. '
        'Weather source selection and station/date validation must come before fitting a model. '
        'Unverified request-type translations will not be modelling inputs.',
        '## Reproduce and inspect',
        '```bash\npython -m src.audit_iris_observation\n```',
        f'Generated tables and the combined observed records are under `{output}` (ignored by Git). '
        'Input fingerprints and rules are in [iris_observation_manifest.json](iris_observation_manifest.json). '
        'The new source profile is [iris_2026_profile.md](iris_2026_profile.md). '
        'Original downloads and the preserved catalog response remain in data/raw/.',
    ]
    Path('reports/iris_observation_windows.md').write_text('\n\n'.join(report) + '\n')
    Path('reports/iris_observation_manifest.json').write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + '\n')
    print(f'Added {added_count:,} observed 2025 registrations; combined {len(cohort):,}; latest closure {cutoff.date()}.')
    print(f'Wrote report, manifest, comparison plot, and four tables under {output}.')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
