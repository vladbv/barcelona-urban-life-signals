"""Compare 2025 official contractual rents with survey-weighted neighbourhood satisfaction."""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import re
import unicodedata
from zipfile import ZipFile
import xml.etree.ElementTree as ET

import numpy as np
import pandas as pd

from src.explore_iris_signals import plt, BARCELONA, style_axis
from src.profile_iris import markdown_table

SURVEY = Path('data/raw/2025_r25041_Serveis_Municipals_Evolucio2025_BD_CSVtext_v1_0.csv')
RENT = Path('data/raw/anual_bcn_lloguer_2026-10-06.xlsx')
RENT_URL = 'https://habitatge.gencat.cat/web/.content/home/dades/estadistiques/01_Estadistiques_de_construccio_i_mercat_immobiliari/03_Mercat_de_lloguer/03_Lloguers_Barcelona_per_districtes_i_barris/anual_bcn_lloguer.xlsx'
SURVEY_URL = 'https://opendata-ajuntament.barcelona.cat/data/dataset/b1cc0c98-9912-4fed-9d75-f577b50a2e9e/resource/df3c3bd9-174c-48fd-831f-874309453039/download'
COLORS = {'Best Value': '#2B7A78', 'Premium Living': '#174C5E',
          'Budget Living': '#B47A21', 'Less for your money': '#B84A3A'}


def read_rent(path: Path) -> pd.DataFrame:
    """Read the inspected one-sheet workbook using the standard library."""
    ns = {'s': 'http://schemas.openxmlformats.org/spreadsheetml/2006/main'}
    with ZipFile(path) as archive:
        strings = [''.join(item.itertext()) for item in ET.fromstring(archive.read('xl/sharedStrings.xml'))]
        cells = {}
        for cell in ET.fromstring(archive.read('xl/worksheets/sheet1.xml')).findall('.//s:c', ns):
            value = cell.find('s:v', ns)
            if value is not None:
                cells[cell.attrib['r']] = strings[int(value.text)] if cell.attrib.get('t') == 's' else value.text
    if cells.get('C5') != '2025' or cells.get('B20') != 'Barris (1)':
        raise ValueError('Rent workbook layout/year changed; inspect before use.')
    table = pd.DataFrame([{'code': int(cells[f'A{i}']), 'neighbourhood': cells[f'B{i}'].strip(),
                           'rent_eur_month': pd.to_numeric(cells.get(f'C{i}'), errors='coerce')}
                          for i in range(21, 94)])
    if table.code.tolist() != list(range(1, 74)):
        raise ValueError('Expected exactly the 73 published neighbourhood codes.')
    return table


def name_key(name: str) -> str:
    # Explicit rent-source extensions; retain their full published names in outputs.
    name = name.split(' - AEI ')[0]
    name = unicodedata.normalize('NFC', name).upper().replace('’', "'")
    return re.sub(r'\s*-\s*', '-', ' '.join(name.split()))


def summarise_survey(frame: pd.DataFrame) -> pd.DataFrame:
    frame = frame.loc[pd.to_numeric(frame.ANY, errors='raise').eq(2025)].copy()
    # Endpoint responses contain explanatory text; nonresponses remain missing.
    score = frame.SATISF_RES_BARRI_0A10.astype('string').str.extract(r'^(10|[0-9])(?:\s*=.*)?$')[0]
    frame['score'] = pd.to_numeric(score, errors='coerce')
    frame['weight'] = pd.to_numeric(frame.PES, errors='raise')
    if not np.isfinite(frame.weight).all() or frame.weight.le(0).any() or frame.BARRI.isna().any():
        raise ValueError('Survey weights or neighbourhood identities need inspection.')
    frame['key'] = frame.BARRI.map(name_key)
    result = []
    for key, group in frame.groupby('key'):
        valid = group.dropna(subset=['score'])
        weights = valid.weight
        result.append({'key': key, 'survey_name': group.BARRI.iloc[0], 'responses': len(group),
                       'valid_responses': len(valid), 'nonresponses': len(group) - len(valid),
                       'effective_n': weights.sum() ** 2 / weights.pow(2).sum() if len(valid) else np.nan,
                       'satisfaction': np.average(valid.score, weights=weights) if len(valid) else np.nan})
    return pd.DataFrame(result)


def classify(rent: float, satisfaction: float, rent_split: float, satisfaction_split: float) -> str:
    if not np.isfinite([rent, satisfaction]).all():
        return 'Insufficient data'
    return ('Premium Living' if rent >= rent_split else 'Best Value') if satisfaction >= satisfaction_split else (
        'Less for your money' if rent >= rent_split else 'Budget Living')


def draw(table: pd.DataFrame, rent_split: float, satisfaction_split: float) -> Path:
    valid = table.dropna(subset=['rent_eur_month', 'satisfaction'])
    fig, ax = plt.subplots(figsize=(15, 10))
    fig.set_facecolor(BARCELONA['paper'])
    xmin, xmax = valid.rent_eur_month.min() - 150, valid.rent_eur_month.max() + 180
    ymin, ymax = valid.satisfaction.min() - .65, min(10, valid.satisfaction.max() + .65)
    ax.set(xlim=(xmin, xmax), ylim=(ymin, ymax))
    for name, x0, x1, y0, y1 in [
        ('Best Value', xmin, rent_split, satisfaction_split, ymax),
        ('Premium Living', rent_split, xmax, satisfaction_split, ymax),
        ('Budget Living', xmin, rent_split, ymin, satisfaction_split),
        ('Less for your money', rent_split, xmax, ymin, satisfaction_split),
    ]:
        ax.fill_between([x0, x1], y0, y1, color=COLORS[name], alpha=.07)
        ax.text(x0 + 20, y1 - .10 if y1 == ymax else y0 + .12, name,
                fontsize=14, weight='bold', color=COLORS[name], va='top' if y1 == ymax else 'bottom')
    ax.axvline(rent_split, color='#6F665D', ls='--', lw=1)
    ax.axhline(satisfaction_split, color='#6F665D', ls='--', lw=1)
    for row in valid.itertuples():
        ax.scatter(row.rent_eur_month, row.satisfaction, s=48,
                   facecolors='white' if row.small_sample else COLORS[row.quadrant],
                   edgecolors=COLORS[row.quadrant], linewidths=1.5, zorder=3)
    style_axis(ax, 'Cost of living vs. quality of life — neighbourhood proxies, 2025',
               'Housing-cost proxy: mean contractual rent (€ / month) → higher cost',
               'Quality-of-life proxy: weighted satisfaction living in the neighbourhood (0–10)')
    fig.subplots_adjust(left=.09, right=.98, top=.90, bottom=.19)
    # Position number labels without moving the actual observations.
    fig.canvas.draw()
    renderer = fig.canvas.get_renderer()
    from matplotlib.transforms import Bbox
    occupied = [Bbox.from_bounds(x-5, y-5, 10, 10) for x,y in
                ax.transData.transform(valid[["rent_eur_month", "satisfaction"]].to_numpy())]
    for row in valid.sort_values(['satisfaction', 'code']).itertuples():
        px, py = ax.transData.transform((row.rent_eur_month, row.satisfaction))
        for radius in (14, 24, 36, 50, 70, 95):
            found = False
            for angle in np.arange(0, 2 * np.pi, np.pi / 4):
                lx, ly = px + radius * np.cos(angle), py + radius * np.sin(angle)
                box = Bbox.from_bounds(lx - 9, ly - 7, 18, 14)
                if not any(box.overlaps(other) for other in occupied):
                    found = True
                    break
            if found:
                break
        if not found:
            raise ValueError('Could not place every point label clearly; adjust the figure layout.')
        occupied.append(box)
        tx, ty = ax.transData.inverted().transform((lx, ly))
        ax.plot([row.rent_eur_month, tx], [row.satisfaction, ty], color='#AAA', lw=.5, zorder=2)
        ax.text(tx, ty, str(row.code), ha='center', va='center', fontsize=8,
                color=BARCELONA['ink'], zorder=4,
                bbox={'facecolor':'white', 'alpha':.8, 'edgecolor':'none', 'pad':.6})
    fig.text(.09, .115, f'Dashed lines: neighbourhood medians (€{rent_split:,.0f}/month; {satisfaction_split:.2f}/10). '
             f'{len(valid)} neighbourhoods plotted.\nNumbers identify neighbourhoods in the accompanying table. Hollow points: fewer than 30 valid responses or effective n < 30.', fontsize=10)
    fig.text(.09, .045, 'Sources: Generalitat / INCASÒL annual rents; Barcelona Municipal Services Survey, 2025.\n'
             'Rent excludes other living costs. Satisfaction is one subjective measure, not a complete quality-of-life index.\n'
             'Quadrants are relative descriptions, not housing recommendations. Small samples and points near boundaries need particular care.', fontsize=9)
    path = Path('reports/figures/neighbourhood_living_quadrants.png')
    fig.savefig(path, dpi=150)
    plt.close(fig)
    return path


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--survey', type=Path, default=SURVEY)
    parser.add_argument('--rent', type=Path, default=RENT)
    parser.add_argument('--download', action='store_true', help='download missing official source files without overwriting originals')
    args = parser.parse_args()
    if args.download:
        from src.data_catalog import download_resource
        for path, url in [(args.survey, SURVEY_URL), (args.rent, RENT_URL)]:
            if not path.exists():
                download_resource([{'id':'source', 'url':url}], 'source', path)
    columns = ['ANY', 'BARRI', 'SATISF_RES_BARRI_0A10', 'PES']
    chunks = [c.loc[c.ANY.eq(2025)] for c in pd.read_csv(args.survey, usecols=columns, chunksize=25000, dtype={'BARRI':'string','SATISF_RES_BARRI_0A10':'string'})]
    survey = summarise_survey(pd.concat(chunks, ignore_index=True))
    rent = read_rent(args.rent)
    rent['key'] = rent.neighbourhood.map(name_key)
    table = rent.merge(survey, on='key', how='outer', validate='one_to_one', indicator=True)
    if not table._merge.eq('both').all():
        raise ValueError('Unmatched neighbourhoods: ' + str(table.loc[table._merge.ne('both'), ['neighbourhood','survey_name']].to_dict('records')))
    table = table.drop(columns=['_merge']).sort_values('code')
    valid = table.dropna(subset=['rent_eur_month', 'satisfaction'])
    rent_split, satisfaction_split = valid[['rent_eur_month','satisfaction']].median()
    table['small_sample'] = table.valid_responses.lt(30) | table.effective_n.lt(30)
    table['quadrant'] = [classify(r.rent_eur_month, r.satisfaction, rent_split, satisfaction_split) for r in table.itertuples()]
    output = Path('data/processed/neighbourhood_living_2025.csv')
    table.to_csv(output, index=False)
    figure = draw(table, rent_split, satisfaction_split)
    display = table[['code','neighbourhood','rent_eur_month','satisfaction','valid_responses','effective_n','small_sample','quadrant']].round(2)
    methodology = (
        'Both axes use 2025 data. Rent is the annual mean monthly contractual rent from deposited INCASÒL rental bonds; '
        'the workbook publishes geolocated contracts and suppresses areas with fewer than six contracts. It does not measure '
        'groceries, utilities, household income or the rents of every existing tenant. Dwelling sizes and rental mix differ. '
        'Satisfaction is our PES-weighted mean of SATISF_RES_BARRI_0A10 in the official Municipal Services Survey. '
        'The endpoint text responses are decoded as 0 and 10; “NO HO SAP”, “NO CONTESTA” and missing responses are excluded. '
        'The unweighted valid response count and Kish effective sample size, (sum of weights)² / sum of squared weights, are shown. '
        'Hollow points flag either count below 30: this is a project caution rule, not an official reliability threshold. '
        'The survey supports grouped-neighbourhood reporting; these individual-neighbourhood estimates are exploratory, '
        'not official neighbourhood rankings, and we have not estimated design-based confidence intervals. '
        'The two AEI extensions in rent names (Poble Sec / Parc Montjuïc and Marina del Prat Vermell / Zona Franca) '
        'are explicitly matched to their residential neighbourhood names; published rent names are retained. '
        'Other names are matched after case, whitespace, apostrophe and hyphen-spacing normalization; all joins must be one-to-one. '
        'Cutoffs are unweighted medians across neighbourhoods with both measures, not citywide household averages. '
        'Ties go to the higher side; missing measures are never assigned a quadrant. Category names are relative labels, '
        'not judgments about residents, a causal claim or a recommendation to rent there.'
    )
    counts = table.quadrant.value_counts().to_dict()
    report = ['# Housing cost and neighbourhood satisfaction, 2025',
              '![Neighbourhood rent and resident satisfaction in four quadrants](figures/neighbourhood_living_quadrants.png)',
              '**How to read it:** moving right means higher monthly rent; moving up means higher resident satisfaction. '
              'The numbered dots identify neighbourhoods in the table below. A point close to a dashed line could change category with a small change in the estimate.',
              f'The dividing lines are **€{rent_split:,.2f}/month** and **{satisfaction_split:.2f}/10**. Counts: ' + ', '.join(f'{k}: {v}' for k,v in counts.items()) + '.',
              'A lower rent can make room in a household budget, while feeling good about the place you live matters too. '
              'These two measures help describe that trade-off, but do not tell us what any particular household can afford or which place will suit it.',
              '## Definitions and limitations', methodology,
              '## Every neighbourhood and its evidence', markdown_table(display),
              '## Sources and reproduction', f'[Official rent workbook]({RENT_URL}); [official survey export]({SURVEY_URL}); '
              '[survey catalog and codebooks](https://opendata-ajuntament.barcelona.cat/data/en/dataset/esm-bcn-evo). '
              'Downloads inspected on 2026-10-06. The survey export includes historical years; only 2025 is used.',
              '```bash\npython -m src.neighbourhood_quadrants --download\n```\n\n'
              'Original files stay in data/raw/. The joined aggregate CSV is written to data/processed/neighbourhood_living_2025.csv. '
              'Source fingerprints are in neighbourhood_living_manifest.json. No IRIS counts enter either axis.']
    Path('reports/neighbourhood_living.md').write_text('\n\n'.join(report)+'\n')
    sources = []
    for path, url in [(args.survey,SURVEY_URL),(args.rent,RENT_URL)]:
        with path.open('rb') as stream:
            sources.append({'path':str(path),'url':url,'sha256':hashlib.file_digest(stream,'sha256').hexdigest()})
    Path('reports/neighbourhood_living_manifest.json').write_text(json.dumps({
        'sources':sources,'year':2025,'rent_median':rent_split,'satisfaction_median':satisfaction_split,
        'neighbourhoods':len(table),'plotted':len(valid),'small_samples':int(table.small_sample.sum()),
        'valid_responses':int(table.valid_responses.sum()),'nonresponses':int(table.nonresponses.sum()),
        'quadrants':counts,'methodology':methodology},ensure_ascii=False,indent=2)+'\n')
    print(f'{len(valid)} neighbourhoods plotted; {table.small_sample.sum()} small samples. Medians: {rent_split:.2f}, {satisfaction_split:.2f}.')
    print(counts)


if __name__ == '__main__':
    main()
