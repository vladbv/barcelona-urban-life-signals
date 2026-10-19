"""Check fixed count models on three earlier months using expanding training windows."""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

import numpy as np
import pandas as pd
import sklearn

from src.explore_iris_signals import plt, style_axis
from src.model_iris_counts import ALPHA, BETA, DRAWS, INPUT, SEED, daily_outcome, evaluate
from src.profile_iris import markdown_table

# Fixed before calculating these scores; no hyperparameter selection follows.
WINDOWS = [('2025-04-01', '2025-04-30'),
           ('2025-06-01', '2025-06-30'),
           ('2025-08-01', '2025-08-31')]
MODELS = ['Weekday average', 'Gamma–Poisson', 'Decision tree']
START = '<!-- BEGIN IRIS VALIDATION -->'
END = '<!-- END IRIS VALIDATION -->'


def validate(daily):
    # Explicitly isolate the original January–August training period.
    development = daily.loc[daily.date.le('2025-08-31')].copy()
    scores, predictions, windows = [], [], []
    for start, end in WINDOWS:
        result = evaluate(development, 30, origin=start, test_end=end)
        month = pd.Timestamp(start).strftime('%B')
        scores.append(result['metrics'].assign(month=month))
        predictions.append(result['predictions'].assign(month=month))
        windows.append({'Month': month,
                        'Train through': str(result['train'].date.max().date()),
                        'Training days': len(result['train']),
                        'Validation start': start, 'Validation end': end,
                        'Validation days': len(result['predictions']),
                        'Coverage (%)': result['coverage'] * 100})
    return pd.concat(scores, ignore_index=True), pd.concat(predictions, ignore_index=True), pd.DataFrame(windows)


def plot(scores, windows, destination):
    months = windows['Month'].tolist()
    x = np.arange(len(months))
    fig, axes = plt.subplots(2, 1, figsize=(9, 6.5), gridspec_kw={'height_ratios': [2, 1]})
    for i, (model, color) in enumerate(zip(MODELS, ['#A3AEB2', '#174C5E', '#B47A21'])):
        values = scores.loc[scores.model.eq(model)].set_index('month').loc[months, 'MAE']
        bars = axes[0].bar(x + (i - 1) * .24, values, width=.24, color=color, label=model)
        axes[0].bar_label(bars, fmt='%.1f', padding=3, fontsize=9)
    axes[0].set_xticks(x, months)
    axes[0].set_ylim(0, scores.MAE.max() * 1.32)
    axes[0].legend(frameon=False, ncol=3, fontsize=9, loc='upper left')
    style_axis(axes[0], 'Does the model help in more than one month?',
               ylabel='Average error (requests/day; lower is better)')
    bars = axes[1].bar(x, windows['Coverage (%)'], width=.5, color='#174C5E')
    axes[1].bar_label(bars, fmt='%.0f%%', padding=3)
    axes[1].axhline(95, color='#B84A3A', linestyle='--', label='Nominal 95% level')
    axes[1].set_xticks(x, months)
    axes[1].set_ylim(0, 110)
    axes[1].text(-.35, 98, 'Nominal 95% level', color='#B84A3A', fontsize=9)
    style_axis(axes[1], 'Check whether the Bayesian intervals capture daily variation',
               xlabel='Validation month in 2025', ylabel='Days inside intervals (%)')
    fig.text(.02, .015, 'IRIS · Cleaning requests marked closed within 30 days · Refit using earlier, matured outcomes only.\nThree retrospective checks; no model tuning or October–December observations in these scores.', fontsize=9)
    fig.tight_layout(rect=(0, .075, 1, 1))
    destination.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(destination, dpi=160)
    plt.close(fig)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--input', type=Path, default=INPUT)
    parser.add_argument('--readme-path', type=Path)
    args = parser.parse_args()
    original = None
    if args.readme_path:
        original = args.readme_path.read_text()
        if original.count(START) != 1 or original.count(END) != 1 or original.index(START) > original.index(END):
            raise ValueError('README needs one ordered validation marker pair.')
    frame = pd.read_csv(args.input, parse_dates=['registration_date', 'closure_date'], low_memory=False)
    scores, predictions, windows = validate(daily_outcome(frame, 30))
    out = Path('data/processed/models')
    out.mkdir(parents=True, exist_ok=True)
    for name, table in [('scores', scores), ('predictions', predictions), ('windows', windows)]:
        table.to_csv(out / f'iris_validation_{name}.csv', index=False)
    plot(scores, windows, Path('reports/figures/iris_temporal_validation.png'))
    errors = scores.pivot(index='month', columns='model', values='MAE')
    wins = int((errors['Decision tree'] < errors['Weekday average']).sum())
    coverage = windows['Coverage (%)']
    finding = (f'The decision tree beats the weekday average in **{wins} of 3 months**. '
               f'The Bayesian model’s nominal 95% intervals contain **{coverage.min():.0f}%–{coverage.max():.0f}%** '
               'of daily counts across these months.')
    interpretation = ('A model that works in one period may disappoint in another. '
                      'For someone anticipating contact with the council, average accuracy and room for busy days both matter. '
                      'These checks assess repeatability; they do not establish readiness for staffing decisions.')
    report = [
        '# Does the model help in more than one month?',
        '![Prediction errors and Bayesian interval coverage in April, June and August](figures/iris_temporal_validation.png)',
        finding, interpretation,
        f'June is difficult for all three models: average errors range from '
        f'{scores.loc[scores.month.eq("June"), "MAE"].min():.1f} to '
        f'{scores.loc[scores.month.eq("June"), "MAE"].max():.1f} requests per day. '
        'The tree’s small advantage that month does not make those predictions reliable. '
        'These scores do not explain the cause of the misses.',
        '## How to read the chart',
        'Top: each bar is the average absolute prediction error (MAE), in requests per day. '
        'A lower bar means smaller misses in that month. Bottom: the share of actual daily counts inside '
        'the Bayesian posterior predictive intervals. The dashed line marks their nominal 95% level. '
        'Three months offer a diagnostic, not a precise estimate of future performance.',
        markdown_table(scores[['month', 'model', 'test_days', 'MAE', 'RMSE']].rename(
            columns={'month': 'Month', 'model': 'Model', 'test_days': 'Validation days'}).round(2)),
        '## Applied Machine Learning: time-based cross-validation',
        'Refit the same three models separately before April, June and August. Each training window begins '
        'January 1 and expands to include only dates whose full 30-day closure window ended before the '
        'validation month. Keep every calendar day, including zero counts. Evaluate the entire next selected month. '
        'Earlier validation months may enter a later training window once their outcomes mature. '
        'The windows therefore overlap in training, and scores are not independent experimental replicates.',
        markdown_table(windows.round(1)),
        'The model settings and features are unchanged from the original benchmark. No search, ranking-based '
        'selection or retuning follows these results. The three windows were fixed before calculating these '
        'scores, but this follow-up was designed after the original October–December results were seen. '
        'It is not a new untouched test. September–December observations are excluded from these fits and scores.',
        '## What the data can support',
        'The outcome remains observed cleaning/collection requests registered in 2025 and marked closed '
        'within 30 days in the two preserved exports. It is neither total demand nor proof of successful repairs. '
        'Historical publication delays and revisions are unknown; date-based label maturity cannot recreate '
        'exactly what data would have been available then. No weather effect or cause of model errors is identified.',
        'Keep the weekday average as a reference in the planned weather comparison. Any more flexible model '
        'should be evaluated with time-aware validation, with a fresh final test required for new performance claims.',
        '## Reproduce',
        '```bash\npython -m src.validate_iris_models --readme-path README.md\n```',
        'Requires the existing observation audit. No new download or dependency. '
        '[Code](../src/validate_iris_models.py) · [Settings and fingerprint](iris_validation_manifest.json) · '
        '[Original model comparison](iris_model_comparison.md).',
    ]
    Path('reports/iris_temporal_validation.md').write_text('\n\n'.join(report) + '\n')
    with args.input.open('rb') as source:
        digest = hashlib.file_digest(source, 'sha256').hexdigest()
    manifest = {'input': {'path': str(args.input), 'sha256': digest}, 'horizon_days': 30,
                'training_start': '2025-01-01', 'windows': windows.to_dict('records'),
                'prior': {'shape': ALPHA, 'rate': BETA}, 'seed': SEED, 'draws': DRAWS,
                'tree': {'max_depth': 3, 'min_samples_leaf': 14},
                'features': ['weekday', 'day_of_year'], 'tuned': False,
                'versions': {'numpy': np.__version__, 'pandas': pd.__version__, 'sklearn': sklearn.__version__},
                'scores': scores.to_dict('records'),
                'limitation': 'Retrospective follow-up designed after the original test was seen; unknown historical publication availability.'}
    Path('reports/iris_validation_manifest.json').write_text(json.dumps(manifest, indent=2) + '\n')
    if original is not None:
        body = ('### Does the model help in more than one month?\n\n'
                '![Earlier-month prediction errors and Bayesian interval coverage](reports/figures/iris_temporal_validation.png)\n\n'
                + finding + '\n\n'
                'This **time-based cross-validation** refits on earlier records before checking April, June and August. '
                'It tests whether the findings repeat before anyone relies on them to anticipate busy days. '
                'These are retrospective checks, with no retuning. '
                '[Read the validation design and limitations](reports/iris_temporal_validation.md).')
        args.readme_path.write_text(original[:original.index(START) + len(START)] + '\n\n' + body
                                   + '\n\n' + original[original.index(END):])
    print(scores.round(2).to_string(index=False))
    print(finding)


if __name__ == '__main__':
    main()
