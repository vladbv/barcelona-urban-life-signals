"""Inspect preserved Open Data BCN daily weather, keys and calendar coverage."""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

import numpy as np
import pandas as pd

from src.data_catalog import download_resource, fetch_json
from src.explore_iris_signals import plt, style_axis
from src.profile_iris import markdown_table

API = 'https://opendata-ajuntament.barcelona.cat/data/api/3/action/package_show?id='
SOURCES = {
    'measurements': ('mesures-estacions-meteorologiques', '2025_MeteoCat_Detall_Estacions.csv'),
    'variables': ('metadades-variables-est-meteo', 'MeteoCat_Metadades.csv'),
    'stations': ('metadades-estacions-meteorologiques', '2020_MeteoCat_Estacions.csv'),
}
VARIABLE = 'ACRÒNIM'
TARGETS = {'TM': ('Mean temperature', '°C'), 'PPT': ('Accumulated rainfall', 'mm')}
NAMES = {'D5': 'Observatori Fabra', 'X2': 'Zoo', 'X4': 'El Raval', 'X8': 'Zona Universitària'}
BEGIN, END = '<!-- BEGIN WEATHER AUDIT -->', '<!-- END WEATHER AUDIT -->'


def paths(snapshot):
    return {kind: (Path(f'data/raw/weather_{kind}_catalog_{snapshot}.json'),
                   Path(f'data/raw/weather_{kind}_{snapshot}.csv')) for kind in SOURCES}


def acquire(snapshot):
    for kind, (catalog, csv) in paths(snapshot).items():
        slug, name = SOURCES[kind]
        if not catalog.exists():
            payload = fetch_json(API + slug)
            if not payload.get('success'):
                raise ValueError('Weather catalog request failed.')
            catalog.parent.mkdir(parents=True, exist_ok=True)
            with catalog.open('x', encoding='utf-8') as stream:
                json.dump(payload, stream, ensure_ascii=False, indent=2)
        payload = json.loads(catalog.read_text())
        resource = next(r for r in payload['result']['resources'] if r.get('name') == name)
        if not csv.exists():
            download_resource(payload['result']['resources'], resource['id'], csv)


def inspect_frames(weather, variables, stations):
    weather = weather.copy()
    key = ['DATA_LECTURA', 'CODI_ESTACIO', VARIABLE]
    if weather.empty or weather[key].isna().any().any() or weather.duplicated(key).any():
        raise ValueError('Weather requires unique, nonmissing date/station/variable keys.')
    weather['DATA_LECTURA'] = pd.to_datetime(weather.DATA_LECTURA, format='%Y-%m-%d', errors='raise')
    if not weather.DATA_LECTURA.dt.year.eq(2025).all():
        raise ValueError('Expected the inspected 2025 daily export.')
    weather['VALOR'] = pd.to_numeric(weather.VALOR, errors='raise')
    if not np.isfinite(weather.VALOR.dropna()).all():
        raise ValueError('Infinite weather values require investigation.')
    if variables[VARIABLE].isna().any() or variables[VARIABLE].duplicated().any():
        raise ValueError('Variable metadata must have unique acronyms.')
    definitions = variables.set_index(VARIABLE)
    for code, (_, unit) in TARGETS.items():
        if code not in definitions.index or definitions.loc[code, 'UNITAT'] != unit:
            raise ValueError('Unexpected temperature/rainfall definition or unit.')
    rain = weather.loc[weather[VARIABLE].eq('PPT'), 'VALOR']
    if rain.lt(0).any():
        raise ValueError('Negative rainfall requires investigation.')
    identity = ['CODI_ESTACIO', 'NOM_ESTACIO', 'ALTITUD', 'LATITUD', 'LONGITUD']
    station_info = stations[identity].drop_duplicates()
    if station_info.CODI_ESTACIO.isna().any() or station_info.CODI_ESTACIO.duplicated().any():
        raise ValueError('Conflicting station identities require investigation.')
    # Sensor rows are not station identities: reduce them before joining.
    weather = weather.merge(station_info, on='CODI_ESTACIO', how='left',
                            validate='many_to_one', indicator='_station')
    weather = weather.merge(variables[[VARIABLE, 'UNITAT']], on=VARIABLE, how='left',
                            validate='many_to_one', indicator='_variable')
    if weather._station.ne('both').any() or weather._variable.ne('both').any():
        raise ValueError('Unmatched station or variable metadata.')
    calendar = pd.date_range('2025-01-01', '2025-12-31')
    panels, summaries = [], []
    for station in station_info.CODI_ESTACIO.sort_values():
        for code, (label, unit) in TARGETS.items():
            selected = weather.loc[weather.CODI_ESTACIO.eq(station) & weather[VARIABLE].eq(code)]
            values = selected.set_index('DATA_LECTURA').VALOR.reindex(calendar)
            present = calendar.isin(selected.DATA_LECTURA)
            panels.append(pd.DataFrame({'date': calendar, 'station': station, 'variable': code,
                                        'value': values.to_numpy(), 'unit': unit, 'record_present': present}))
            summaries.append({'Station': station, 'Variable': label, 'Unit': unit,
                              'Recorded days': int(present.sum()), 'Numeric days': int(values.notna().sum()),
                              'Absent dates': int((~present).sum()),
                              'Null values': int((present & values.isna()).sum())})
    naive_rows = int(weather.CODI_ESTACIO.map(stations.CODI_ESTACIO.value_counts()).sum())
    return pd.concat(panels, ignore_index=True), pd.DataFrame(summaries), station_info, naive_rows


def plot_coverage(summary, destination):
    codes = sorted(summary.Station.unique())
    y = np.arange(len(codes))
    fig, ax = plt.subplots(figsize=(9, 4.8))
    for i, (code, (label, _)) in enumerate(TARGETS.items()):
        counts = summary.loc[summary.Variable.eq(label)].set_index('Station').loc[codes, 'Numeric days']
        bars = ax.barh(y + (i - .5) * .32, counts, height=.30,
                       color=['#B47A21', '#174C5E'][i], label=label)
        ax.bar_label(bars, labels=[f'{n}/365' for n in counts], padding=5, fontsize=10)
    ax.set_yticks(y, [f'{NAMES.get(code, code)} ({code})' for code in codes])
    ax.set_ylim(len(codes) - .4, -.8)
    ax.set_xlim(0, 425)
    ax.legend(frameon=False, loc='upper right', ncol=2, fontsize=9)
    style_axis(ax, 'Check weather coverage before explaining city requests',
               'Days with a numeric weather record in 2025')
    fig.text(.02, .015, 'Open Data BCN · Four stations listed in the 2020 metadata. Zero records does not mean zero rainfall.\nCoverage counts do not certify measurement quality or neighbourhood representativeness.', fontsize=9)
    fig.tight_layout(rect=(0, .12, 1, 1))
    destination.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(destination, dpi=160)
    plt.close(fig)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--snapshot', default='2026-10-26', help='Preserved snapshot date (YYYY-MM-DD).')
    parser.add_argument('--download', action='store_true', help='Download missing sources only; never overwrite raw files.')
    parser.add_argument('--readme-path', type=Path)
    args = parser.parse_args()
    if pd.Timestamp(args.snapshot).strftime('%Y-%m-%d') != args.snapshot:
        parser.error('Use a YYYY-MM-DD snapshot date.')
    original = args.readme_path.read_text() if args.readme_path else None
    if original is not None and (original.count(BEGIN) != 1 or original.count(END) != 1 or original.index(BEGIN) > original.index(END)):
        raise ValueError('README requires one ordered weather-audit marker pair.')
    if args.download:
        acquire(args.snapshot)
    inputs = paths(args.snapshot)
    frames = {kind: pd.read_csv(csv, dtype={'CODI_ESTACIO': str}) for kind, (_, csv) in inputs.items()}
    daily, summary, stations, naive_rows = inspect_frames(frames['measurements'], frames['variables'], frames['stations'])
    out = Path('data/processed/weather'); out.mkdir(parents=True, exist_ok=True)
    daily.to_csv(out / 'weather_2025_calendar.csv', index=False)
    summary.to_csv(out / 'weather_2025_coverage.csv', index=False)
    plot_coverage(summary, Path('reports/figures/weather_coverage.png'))
    count = len(frames['measurements'])
    sources = {}
    for kind, (catalog, csv) in inputs.items():
        payload = json.loads(catalog.read_text())['result']
        resource = next(r for r in payload['resources'] if r.get('name') == SOURCES[kind][1])
        files = []
        for path in (catalog, csv):
            with path.open('rb') as stream:
                digest = hashlib.file_digest(stream, 'sha256').hexdigest()
            files.append({'path': str(path), 'sha256': digest})
        sources[kind] = {'catalog_url': API + SOURCES[kind][0], 'resource_id': resource['id'],
                         'download_url': resource['url'], 'license': payload.get('license_title'),
                         'columns': list(frames[kind].columns), 'rows': len(frames[kind]), 'files': files}
    manifest = {'snapshot': args.snapshot, 'sources': sources, 'coverage': summary.to_dict('records'),
                'join_key': ['DATA_LECTURA', 'CODI_ESTACIO', VARIABLE],
                'naive_station_join_rows': naive_rows, 'safe_join_rows': count,
                'limits': ['Station metadata is dated 2020.', 'Daily boundaries/time zone not verified.',
                           'No measurement quality flag in this export.', 'No IRIS-weather join or association fitted.']}
    Path('reports/weather_manifest.json').write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + '\n')
    missing = daily.loc[daily.station.eq('D5') & daily.variable.eq('TM') & ~daily.record_present, 'date']
    report = [
        '# Weather context starts with trustworthy joins',
        'Rain and heat are plausible context for public-space concerns. Before asking whether they coincide '
        'with reported requests, establish what the weather files actually measure.',
        '![Daily rain and temperature coverage by station](figures/weather_coverage.png)',
        markdown_table(summary),
        'Bars count dates with numeric values, not rainy days. Zoo is present only in the older station '
        'metadata; zero observations is not evidence of dry weather or proof that the station was inactive. '
        'Fabra temperature has absent dates: ' + ', '.join(missing.dt.strftime('%Y-%m-%d')) + '.',
        '## Data Mining: inspect the grain before joining',
        f'The daily export has **{count:,} rows** and five columns. Its unique key is date + station + '
        f'variable. Station metadata has **{len(frames["stations"])} sensor rows**, describing '
        f'**{len(stations)} station identities**. Joining it on station code alone would produce '
        f'**{naive_rows:,} rows**, repeating observations. The audit checks station identity consistency, '
        'reduces metadata to one identity per station and enforces many-to-one joins. Missing calendar '
        'records stay missing, never zero-filled.',
        'Weather columns: ' + ', '.join(f'`{c}`' for c in frames['measurements'].columns) + '. '
        '`DATA_LECTURA` is the daily label; `DATA_EXTREM` supplies an extreme-value time where present. '
        'A missing extreme time is not itself a missing daily temperature or rainfall measurement.',
        markdown_table(frames['variables'].loc[frames['variables'][VARIABLE].isin(TARGETS)]),
        '## Station choice and limits',
        markdown_table(stations.rename(columns={'CODI_ESTACIO': 'Station', 'NOM_ESTACIO': 'Published name',
                                                'ALTITUD': 'Altitude (m)', 'LATITUD': 'Latitude', 'LONGITUD': 'Longitude'})),
        'El Raval (X4) is the provisional primary station for the next city-level comparison: its published '
        'location is urban and both selected variables cover 365 dates. Zona Universitària (X8) offers a '
        'second complete series for sensitivity checks. Fabra sits at a different elevation and has one '
        'temperature gap. This choice does not make any station representative of all 73 neighbourhoods. '
        'The 2020 metadata cannot certify unchanged locations, sensors or operating status in 2025.',
        'The export contains no measurement-quality/representativeness flag. '
        '[Meteocat describes such flags for its daily XEMA source](https://www.meteo.cat/wpweb/serveis/dades-obertes/). '
        'Record presence therefore cannot be treated as a quality certificate. The exact daily aggregation '
        'boundary and time zone are not established by these three files. Verify them before aligning weather '
        'with IRIS registration dates; do not infer a local calendar day from a date-only label.',
        '## Next comparison, not a result yet',
        'After resolving day alignment and quality provenance, join one selected station-day to the full '
        'IRIS daily calendar with one-to-one validation. Keep missing weather visible and use a second '
        'station as a sensitivity check. Any association analysis needs weekday/month controls and '
        'reporting-channel checks. No weather effect, causal claim or forecast improvement is established here.',
        '## Reproduce and attribute',
        '```bash\npython -m src.audit_weather --download --snapshot ' + args.snapshot + ' --readme-path README.md\n```',
        'Omit `--download` for an offline rebuild. On a later download, use its actual date as `--snapshot`; '
        'the server does not guarantee historical file versions. Raw files are never overwritten. '
        'Derived calendar and coverage CSVs live in `data/processed/weather/`.',
        'Source: Barcelona City Council / Open Data BCN, meteorological observations attributed to '
        'Servei Meteorològic de Catalunya (XEMA). Catalog license: CC BY 4.0. '
        '[Measurements](https://opendata-ajuntament.barcelona.cat/data/en/dataset/mesures-estacions-meteorologiques) · '
        '[Variable definitions](https://opendata-ajuntament.barcelona.cat/data/en/dataset/metadades-variables-est-meteo) · '
        '[Stations](https://opendata-ajuntament.barcelona.cat/data/en/dataset/metadades-estacions-meteorologiques) · '
        '[Fingerprints and schemas](weather_manifest.json) · [Audit code](../src/audit_weather.py).',
    ]
    Path('reports/weather_source_audit.md').write_text('\n\n'.join(report) + '\n')
    if original is not None:
        body = ('## Before explaining the weather, check the data\n\n'
                'Rain and heat may help contextualise public-space requests. First, I checked the official '
                'weather export’s coverage and how its tables fit together.\n\n'
                '![Days with rain and temperature records at Barcelona weather stations](reports/figures/weather_coverage.png)\n\n'
                '**Data Mining in practice: join cardinality.** Joining repeated station metadata directly '
                f'would inflate **{count:,} observations to {naive_rows:,} rows**. '
                'The audit enforces one station identity per join and preserves missing days.\n\n'
                'Three stations supply 2025 records; the older list also names Zoo, which has none in this export. '
                '**Missing records are not zero rainfall.** Daily time boundaries and measurement quality still '
                'need verification before linking weather to IRIS. '
                '[Read the source audit and station choice](reports/weather_source_audit.md).')
        args.readme_path.write_text(original[:original.index(BEGIN) + len(BEGIN)] + '\n\n' + body + '\n\n' + original[original.index(END):])
    print(summary.to_string(index=False))
    print(f'Weather observations: {count}; naive station join: {naive_rows}; safe join: {count}.')


if __name__ == '__main__':
    main()
