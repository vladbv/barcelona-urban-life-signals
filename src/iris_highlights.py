"""Small, readable README charts drawn from the same validated summary tables."""
from pathlib import Path
import os
import textwrap

import pandas as pd
from matplotlib.ticker import StrMethodFormatter

from src.explore_iris_signals import plt
from src.iris_signals import MISSING


def highlight_chart(labels, values, xlabel: str, path: Path) -> None:
    """Use direct labels and large type; the README supplies the finding title."""
    fig, ax = plt.subplots(figsize=(9, 3.7))
    positions = range(len(labels))
    bars = ax.barh(positions, values, color=['#174C5E'] * (len(labels) - 1) + ['#A3AEB2'], height=.55)
    ax.set_yticks(list(positions), ['\n'.join(textwrap.wrap(label, 26)) for label in labels], fontsize=13)
    ax.invert_yaxis()
    ax.bar_label(bars, labels=[f'{value:,.0f}' for value in values], padding=8, fontsize=13)
    ax.set_xlim(0, max(values) * 1.22)
    ax.set_xlabel(xlabel, fontsize=12, labelpad=12)
    ax.xaxis.set_major_formatter(StrMethodFormatter('{x:,.0f}'))
    ax.tick_params(axis='both', length=0, labelsize=12)
    ax.spines[['top', 'right', 'left']].set_visible(False)
    ax.spines['bottom'].set_color('#CDD3D6')
    ax.grid(axis='x', color='#E9ECEF')
    ax.set_axisbelow(True)
    fig.text(.02, .025, 'Source: Open Data BCN · IRIS · Registered and marked closed in 2025', fontsize=10, color='#52616A')
    fig.tight_layout(rect=(0, .09, 1, 1))
    path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(path, dpi=180, facecolor='white')
    plt.close(fig)


def readme_highlights(tables: dict[str, pd.DataFrame], directory: Path, parent: Path) -> str:
    areas = tables['areas'].set_index('area')
    total = int(areas.requests.sum())
    cleaning = int(areas.loc["Recollida i neteja de l'espai urbà", 'requests'])
    maintenance = int(areas.loc["Manteniment de l'espai urbà", 'requests'])
    weekday = tables['weekday'].set_index('weekday')
    work = weekday.loc[['Monday','Tuesday','Wednesday','Thursday','Friday']]
    weekend = weekday.loc[['Saturday','Sunday']]
    work_mean, weekend_mean = work.requests.sum() / work.calendar_days.sum(), weekend.requests.sum() / weekend.calendar_days.sum()
    missing = int(tables['districts'].set_index('district').loc[MISSING, 'requests'])
    specs = [
        ('topics', ['Waste collection and street cleaning', 'Public-space maintenance', 'All other request topics'],
         [cleaning, maintenance, total-cleaning-maintenance], 'Number of recorded requests'),
        ('weekdays', ['Monday–Friday', 'Saturday–Sunday'], [work_mean, weekend_mean], 'Average recorded requests per calendar day'),
        ('location', ['District recorded', 'No district recorded'], [total-missing, missing], 'Number of recorded requests'),
    ]
    images = {}
    for key, labels, values, xlabel in specs:
        path = directory / f'iris_highlight_{key}.png'
        highlight_chart(labels, values, xlabel, path)
        images[key] = os.path.relpath(path, parent)
    return '\n\n'.join([
        '## Three findings',
        f'These charts use **{total:,} requests registered and marked closed in 2025**. '
        'They describe contact with the council, not every problem in the city.',
        f'### 1. Cleaning and maintenance account for {(cleaning+maintenance)/total:.0%} of requests',
        f'![Request counts: cleaning {cleaning:,}; maintenance {maintenance:,}; all other topics {total-cleaning-maintenance:,}.]({images["topics"]})',
        f'**{cleaning+maintenance:,} requests concern the upkeep of shared public spaces.** '
        'The bars count requests by topic; “all other” combines the remaining categories.',
        'Streets and pavements are part of everyday life. Their prominence identifies a concrete topic for further study. '
        '**More reports do not necessarily mean more severe problems:** several requests may concern the same issue.',
        f'### 2. Weekdays average {work_mean/weekend_mean:.1f} times as many requests as weekends',
        f'![Daily average requests: {work_mean:,.0f} on weekdays and {weekend_mean:,.0f} at weekends.]({images["weekdays"]})',
        f'**{work_mean:,.0f} requests per weekday, compared with {weekend_mean:,.0f} per weekend day.** '
        'Each total is divided by the number of days in its group, so five weekdays are not compared directly with two weekend days.',
        'When assessing a busy day, compare it with similar weekdays first. '
        '**This measures when requests enter IRIS**, not when problems begin or why people choose to report.',
        f'### 3. {missing/total:.0%} of requests have no recorded district',
        f'![Requests with a district: {total-missing:,}; without a district: {missing:,}.]({images["location"]})',
        f'**A district-only map would leave out {missing:,} requests.** '
        'Keeping those records visible prevents a partial map from looking like a complete account.',
        'Some requests concern administrative services rather than a specific place. '
        '**Missing district does not automatically mean an error**, and district counts cannot rank neighbourhood quality.',
        '[Explore all 13 plots, English category labels and detailed interpretations](reports/iris_signal_summary.md).',
    ])
