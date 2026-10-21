"""A fixed temporal benchmark for observed cleaning requests, with Bayesian model checks."""
from __future__ import annotations

import argparse
import hashlib
import json
import math
from pathlib import Path

import numpy as np
import pandas as pd
import sklearn
from sklearn.tree import DecisionTreeRegressor, export_text

from src.explore_iris_signals import plt, style_axis
from src.profile_iris import markdown_table

INPUT = Path('data/processed/observation_audit/iris_observed_2025_records.csv')
ORIGIN = pd.Timestamp('2025-10-01')
CUTOFF = pd.Timestamp('2026-03-31')
AREA = "Recollida i neteja de l'espai urbà"
ALPHA, BETA = 2.0, 0.01  # Gamma shape and RATE; mean=200, SD=141.4.
DRAWS, SEED = 50000, 20261016
FEATURES = ['weekday', 'day_of_year']


def daily_outcome(frame: pd.DataFrame, horizon: int) -> pd.DataFrame:
    if horizon not in (30, 90):
        raise ValueError('Use the inspected 30- or 90-day outcome.')
    if frame.empty or not frame.area.eq(AREA).any():
        raise ValueError('Expected observed records with the inspected cleaning category.')
    if frame.fitxa_id.isna().any() or frame.fitxa_id.duplicated().any():
        raise ValueError('Missing or duplicate request identifiers.')
    dates = frame[['registration_date', 'closure_date']]
    if dates.isna().any().any() or not frame.registration_date.dt.year.eq(2025).all():
        raise ValueError('Expected valid dates and 2025 registrations.')
    lag = (frame.closure_date - frame.registration_date).dt.days
    if lag.lt(0).any() or not lag.eq(frame.closure_lag_days).all() or frame.closure_date.gt(CUTOFF).any():
        raise ValueError('Invalid lag or closure outside the inspected coverage.')
    selected = frame.loc[frame.area.eq(AREA) & lag.le(horizon)]
    calendar = pd.date_range('2025-01-01', '2025-12-31', name='date')
    if (calendar + pd.Timedelta(days=horizon) > CUTOFF).any():
        raise ValueError('Insufficient follow-up coverage.')
    daily = selected.groupby('registration_date').size().reindex(calendar, fill_value=0).rename('count').reset_index()
    daily['weekday'] = daily.date.dt.dayofweek
    daily['day_of_year'] = daily.date.dt.dayofyear
    return daily


def split_days(daily: pd.DataFrame, horizon: int, *, origin=ORIGIN, test_end=None):
    # A full label window must finish BEFORE the forecast origin, including zero-count days.
    origin = pd.Timestamp(origin)
    test_end = daily.date.max() if test_end is None else pd.Timestamp(test_end)
    if test_end < origin or horizon not in (30, 90):
        raise ValueError('Use an ordered evaluation period and a 30- or 90-day horizon.')
    train = daily.loc[daily.date + pd.Timedelta(days=horizon) < origin].copy()
    test = daily.loc[daily.date.between(origin, test_end)].copy()
    if train.empty or test.empty or set(train.weekday) != set(range(7)):
        raise ValueError('Need nonempty periods and all weekdays in training.')
    return train, test


def gamma_update(counts, alpha=ALPHA, beta=BETA):
    y = np.asarray(counts, dtype=float)
    if (y.ndim != 1 or y.size == 0 or not np.isfinite(y).all()
            or (y < 0).any() or (y != np.floor(y)).any()
            or not np.isfinite([alpha, beta]).all() or alpha <= 0 or beta <= 0):
        raise ValueError('Use nonnegative integer counts and positive prior parameters.')
    return alpha + y.sum(), beta + len(y)


def evaluate(daily: pd.DataFrame, horizon: int, *, origin=ORIGIN, test_end=None):
    train, test = split_days(daily, horizon, origin=origin, test_end=test_end)
    model = DecisionTreeRegressor(max_depth=3, min_samples_leaf=14, random_state=SEED)
    model.fit(train[FEATURES], train['count'])
    predictions = test[['date', 'weekday', 'count']].copy()
    means = train.groupby('weekday')['count'].mean()
    predictions['Weekday average'] = test.weekday.map(means)
    predictions['Decision tree'] = model.predict(test[FEATURES])
    rng = np.random.default_rng(SEED + horizon)
    posterior, sensitivity, checks = [], [], []
    for weekday, group in train.groupby('weekday'):
        y = group['count'].to_numpy()
        a, b = gamma_update(y)
        rates = rng.gamma(a, 1 / b, DRAWS)
        future = rng.poisson(rates)
        lo, hi = np.quantile(future, [.025, .975], method='inverted_cdf')
        mask = predictions.weekday.eq(weekday)
        predictions.loc[mask, 'Gamma–Poisson'] = a / b
        predictions.loc[mask, 'predictive_low'] = lo
        predictions.loc[mask, 'predictive_high'] = hi
        posterior.append({'weekday': int(weekday), 'train_days': len(y), 'sum_counts': int(y.sum()),
                          'posterior_shape': a, 'posterior_rate': b, 'posterior_mean': a/b,
                          'rate_low': float(np.quantile(rates,.025)), 'rate_high': float(np.quantile(rates,.975)),
                          'predictive_low': int(lo), 'predictive_high': int(hi),
                          'mc_mean_standard_error': float(rates.std(ddof=1)/np.sqrt(DRAWS))})
        for mean in (50, 200, 500):
            sa, sb = gamma_update(y, 2, 2/mean)
            sensitivity.append({'weekday':int(weekday),'prior_mean':mean,'posterior_mean':sa/sb})
        # Joint replicated training samples share one rate draw per replicate.
        replicate_rates = rng.gamma(a, 1/b, 4000)
        replicas = rng.poisson(replicate_rates[:,None], size=(4000,len(y)))
        observed = y.var(ddof=1) / y.mean() if y.mean() else 0.0
        replicate_dispersion = replicas.var(axis=1,ddof=1) / np.maximum(replicas.mean(axis=1),1e-12)
        checks.append({'weekday':int(weekday),'observed_variance_to_mean':observed,
                       'replicated_dispersion_95th':float(np.quantile(replicate_dispersion,.95)),
                       'replicates_at_least_observed':int((replicate_dispersion>=observed).sum()),'replicates':4000})
    metrics = []
    for name in ['Weekday average','Gamma–Poisson','Decision tree']:
        error = predictions[name] - predictions['count']
        metrics.append({'horizon_days':horizon,'model':name,'test_days':len(test),
                        'MAE':float(error.abs().mean()),'RMSE':float(np.sqrt(error.pow(2).mean()))})
    coverage = predictions['count'].between(predictions.predictive_low,predictions.predictive_high).mean()
    return {'train':train,'predictions':predictions,'metrics':pd.DataFrame(metrics),
            'posterior':pd.DataFrame(posterior),'sensitivity':pd.DataFrame(sensitivity),
            'checks':pd.DataFrame(checks),'coverage':float(coverage),'tree':model}


def gamma_logpdf(x, a, b):
    return a*np.log(b)-math.lgamma(a)+(a-1)*np.log(x)-b*x


def figures(result, directory):
    row = result['posterior'].set_index('weekday').loc[0]  # Monday chosen in advance.
    a,b = row.posterior_shape,row.posterior_rate
    fig,axes = plt.subplots(2,1,figsize=(9,7))
    x = np.linspace(.01,800,2000)
    axes[0].plot(x,np.exp(gamma_logpdf(x,ALPHA,BETA)),color='#B47A21',lw=2)
    style_axis(axes[0],'Prior: a broad starting assumption for Monday counts',
               'Expected observed cleaning requests per Monday','Prior density')
    sd=np.sqrt(a)/b
    x=np.linspace(max(.01,a/b-5*sd),a/b+5*sd,1500)
    likelihood=row.sum_counts*np.log(x)-row.train_days*x
    post=gamma_logpdf(x,a,b)
    axes[1].plot(x,np.exp(likelihood-likelihood.max()),color='#B47A21',lw=3,label='Likelihood: support from training counts')
    axes[1].plot(x,np.exp(post-post.max()),color='#174C5E',lw=2,ls='--',label='Posterior: prior updated by those counts')
    axes[1].axvspan(row.rate_low,row.rate_high,color='#174C5E',alpha=.1)
    style_axis(axes[1],'After observing Mondays, likelihood and posterior nearly overlap',
               'Expected observed cleaning requests per Monday (zoomed scale)','Relative height (each peak = 1)')
    axes[1].legend(frameon=False,fontsize=9)
    fig.text(.02,.015,'IRIS · 30-day closure outcome · Shading: model-conditional 95% credible interval for the rate.\nA precise rate estimate does not guarantee reliable predictions. The next chart tests that distinction.',fontsize=9)
    fig.tight_layout(rect=(0,.08,1,1));fig.savefig(directory/'iris_bayesian_update.png',dpi=160);plt.close(fig)
    p=result['predictions'];m=result['metrics']
    fig,axes=plt.subplots(2,1,figsize=(10,8),gridspec_kw={'height_ratios':[2,1]})
    axes[0].fill_between(p.date,p.predictive_low,p.predictive_high,color='#174C5E',alpha=.18,label='Nominal 95% posterior predictive interval')
    axes[0].plot(p.date,p['Gamma–Poisson'],color='#174C5E',lw=1,label='Bayesian predictive mean')
    axes[0].scatter(p.date,p['count'],s=15,color='#B84A3A',label='Observed test-day count',zorder=3)
    style_axis(axes[0],f'Only {result["coverage"]:.0%} of later days fall inside the model’s 95% intervals',
               'Registration date: October–December 2025 test','Cleaning requests closed within 30 days')
    axes[0].set_ylim(0,p['count'].max()*1.25);axes[0].legend(frameon=False,fontsize=8,loc='upper left')
    bars=axes[1].barh(m.model,m.MAE,color=['#A3AEB2','#174C5E','#B47A21'])
    axes[1].bar_label(bars,fmt='%.1f',padding=6)
    axes[1].set_xlim(0,m.MAE.max()*1.2);axes[1].invert_yaxis()
    style_axis(axes[1],'A machine-learning model must earn its place against a simple baseline',
               'Mean absolute error: requests per day (lower is better)')
    fig.text(.02,.015,'Open Data BCN · Two inspected closure exports · Fixed October–December 2025 test; no test-set tuning.\nRetrospective benchmark of selected reported activity, not a validated operational forecast or measure of service quality.',fontsize=9)
    fig.tight_layout(rect=(0,.075,1,1));fig.savefig(directory/'iris_model_holdout.png',dpi=160);plt.close(fig)


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--input',type=Path,default=INPUT)
    parser.add_argument('--readme-path',type=Path)
    args=parser.parse_args()
    frame=pd.read_csv(args.input,parse_dates=['registration_date','closure_date'],low_memory=False)
    results={h:evaluate(daily_outcome(frame,h),h) for h in (30,90)}
    out=Path('data/processed/models');out.mkdir(parents=True,exist_ok=True)
    for h,r in results.items():
        for key in ['train','predictions','metrics','posterior','sensitivity','checks']:
            r[key].to_csv(out/f'iris_{h}d_{key}.csv',index=False)
    directory=Path('reports/figures');directory.mkdir(parents=True,exist_ok=True)
    figures(results[30],directory)
    metrics=pd.concat([r['metrics'] for r in results.values()],ignore_index=True)
    r=results[30]; monday=r['posterior'].iloc[0]
    text=[
        '# What the models learn—and what they miss',
        '**Question:** can simple models describe and predict daily observed cleaning requests that are marked closed within 30 days?',
        '## Prior, likelihood and posterior: an actual calculation',
        '![Monday prior, likelihood and posterior](figures/iris_bayesian_update.png)',
        f'The Monday rate changes from a prior mean of 200 to a posterior mean of {monday.posterior_mean:.1f} requests per day. '
        f'The model-conditional 95% credible interval is {monday.rate_low:.1f}–{monday.rate_high:.1f}. '
        'The likelihood and posterior nearly overlap because the training data outweigh this broad prior. '
        'The two panels use different x ranges; the lower curves are each scaled to peak at one. A likelihood curve is not a probability distribution over the rate.',
        'For each weekday separately, daily counts are assumed conditionally independent Poisson(lambda). '
        'The prior is Gamma(shape=2, rate=0.01), with mean 200 and SD about 141. It is an illustrative assumption, not elicited knowledge. '
        'After n training days with S total requests, the posterior is Gamma(2 + S, 0.01 + n). '
        'NumPy uses a scale parameter, so the implementation passes 1/rate. The posterior predictive distribution mixes '
        'Poisson counts over Gamma rate draws, incorporating both rate uncertainty and observation variability.',
        '## Test the uncertainty, not just the central estimate',
        '![Held-out observations, predictive intervals and model errors](figures/iris_model_holdout.png)',
        f'Only **{r["coverage"]:.1%}** of the 92 test days fall inside the nominal 95% predictive intervals. '
        'A narrow credible interval for a mean rate is therefore not evidence that daily counts are well predicted. '
        'Unexpected reporting spikes matter if someone uses the estimates to anticipate incoming requests. '
        'The interval check makes this limitation visible before any operational use.',
        markdown_table(metrics.round(2)),
        'MAE is the average absolute difference between predicted and observed requests per day; RMSE gives larger misses more weight. '
        'The weekday-average baseline and Bayesian predictive means are almost identical because the prior has little influence. '
        'The decision tree can learn calendar splits, but extra flexibility need not improve performance on later dates.',
        '## Design fixed before inspecting test performance',
        'Outcome: exact published AREA label “Recollida i neteja de l’espai urbà” in the two audited exports, '
        'registration dates in 2025, and closure lag <=30 days including zero and day 30. '
        'All 365 calendar dates are retained; a zero means zero qualifying records observed in these snapshots. '
        'Unknown unpublished records and still-open requests remain outside the target.',
        'Forecast origin: 2025-10-01. Test: all October–December dates. Train only on dates whose full closure window ends '
        '**before** the origin: January–August for 30 days. September is excluded from training to prevent immature labels. '
        'Models are fitted once and held fixed throughout the test. The 90-day sensitivity uses the same origin and test dates, '
        'with training ending July 2 so every training outcome has matured. It changes both the target and training length; '
        'it is not a pure comparison of follow-up periods. Neither run was used for tuning.',
        'Calendar features known in advance: weekday (0–6) and day of year. DecisionTreeRegressor uses max_depth=3, '
        'min_samples_leaf=14 and a fixed seed; no scaling, target-derived features or activation function is required. '
        'The tree uses squared-error splits and cannot extrapolate seasonal trends beyond its training range. '
        'There is no hyperparameter search and no independent replication across years.',
        'This is a **retrospective temporal benchmark**, not a reconstruction of data available in production on that day: '
        'the exports were downloaded later, so revisions and publication delays are not known. '
        'The recorded-date maturity rule prevents one kind of label leakage; it cannot establish historical publication availability.',
        '## Data mining and posterior predictive checks',
        'Training counts are profiled by weekday. Compare their variance-to-mean ratio with 4,000 replicated training samples '
        'from the fitted Gamma–Poisson model. Each replicate shares a sampled rate across its days. '
        'A much larger observed ratio indicates variation the constant weekday-rate model does not reproduce; it does not identify a cause. '
        'The replicate exceedance counts are simulation diagnostics, not classical significance tests.',
        markdown_table(r['checks'].round(2)),
        '## Prior sensitivity and simulation accuracy',
        'Repeat the conjugate update with shape 2 and prior means 50, 200 and 500. These priors all have small effective '
        'exposure relative to the training data, so this is a limited sensitivity check, not proof that every prior would agree.',
        markdown_table(r['sensitivity'].round(2)),
        'Each weekday uses 50,000 seeded Gamma draws and corresponding Poisson draws for intervals. '
        'Point forecasts use exact posterior means. The table below records Monte Carlo standard error of each simulated mean. '
        'Interval endpoints also have simulation error; the fixed seed makes the displayed results reproducible.',
        markdown_table(r['posterior'].round(3)),
        '## Inspect the fitted tree',
        '```text\n'+export_text(r['tree'],feature_names=FEATURES)+'```',
        '## Reproduce',
        '```bash\npython -m src.audit_iris_observation\npython -m src.model_iris_counts --readme-path README.md\n```',
        'The original descriptive charts still use the 2025 closure-year group. These model results use the separate '
        'combined-export, fixed-window cleaning outcome. No weather effect, causality or citywide demand claim is made. '
        'Next: investigate time-varying rates and overdispersion using validation periods chosen within training data. '
        'Treat this test quarter as already seen in any further development.',
        '[Decision tree reference](https://scikit-learn.org/stable/modules/generated/sklearn.tree.DecisionTreeRegressor.html) · '
        '[NumPy Gamma draws](https://numpy.org/doc/stable/reference/random/generated/numpy.random.Generator.gamma.html) · '
        '[NumPy Poisson draws](https://numpy.org/doc/stable/reference/random/generated/numpy.random.Generator.poisson.html). '
        'Inputs and settings: [manifest](iris_model_manifest.json). Aggregate outputs: data/processed/models/.',
    ]
    Path('reports/iris_model_comparison.md').write_text('\n\n'.join(text)+'\n')
    with args.input.open('rb') as f: digest=hashlib.file_digest(f,'sha256').hexdigest()
    manifest={'input':{'path':str(args.input),'sha256':digest},'source_audit':'reports/iris_observation_manifest.json',
              'origin':str(ORIGIN.date()),'observed_coverage_end':str(CUTOFF.date()),'area':AREA,
              'prior':{'shape':ALPHA,'rate':BETA},'seed':SEED,'draws':DRAWS,'tree':{'max_depth':3,'min_samples_leaf':14},
              'features':FEATURES,'versions':{'numpy':np.__version__,'pandas':pd.__version__,'sklearn':sklearn.__version__},
              'runs':{str(h):{'train_start':str(v['train'].date.min().date()),'train_end':str(v['train'].date.max().date()),
                             'train_days':len(v['train']),'test_days':len(v['predictions']),'coverage':v['coverage']} for h,v in results.items()},
              'metrics':metrics.to_dict('records'),'selection_warning':'Selected observed closed requests; unknown publication delays and incomplete coverage. Retrospective test, not operational validation.'}
    Path('reports/iris_model_manifest.json').write_text(json.dumps(manifest,indent=2,ensure_ascii=False)+'\n')
    if args.readme_path:
        original=args.readme_path.read_text();start='<!-- BEGIN IRIS MODEL FINDINGS -->';end='<!-- END IRIS MODEL FINDINGS -->'
        if original.count(start)!=1 or original.count(end)!=1 or original.index(start)>original.index(end):
            raise ValueError('README needs one correctly ordered model-findings marker pair.')
        scores=r['metrics'].set_index('model').MAE
        sensitivity_scores=results[90]['metrics'].set_index('model').MAE
        body=f'''## A precise average can still miss a busy day

This experiment uses **cleaning requests marked closed within 30 days**, combining
the two audited exports. It is a different group from the descriptive charts above.

![Observed later counts, Bayesian predictive intervals and errors from three models](reports/figures/iris_model_holdout.png)

**Read the chart:** dots are observed daily counts; the shaded band is the
Bayesian model’s predicted range. The lower bars compare average errors.

**The Bayesian model’s nominal 95% intervals cover only {r['coverage']:.0%} of test days.**
This is a **calibration** check: a well-calibrated 95% range should contain
roughly 95% of new daily counts over repeated predictions. Here, too many days
fall outside it for the range to be dependable.

The *prior* describes possible mean daily counts. The *Poisson likelihood*
measures how well each mean explains the training counts. The *posterior* updates
our uncertainty about that mean; the *posterior predictive distribution* also
includes variation from one day to another.

<details>
<summary>Worked Bayesian example: estimating an average versus predicting a day</summary>

For Mondays, the illustrative **Gamma prior** has mean 200 requests.
The **Poisson likelihood** uses {int(monday.sum_counts):,} qualifying requests across
{int(monday.train_days)} training Mondays. **Conjugate updating** gives a Gamma posterior
with mean **{monday.posterior_mean:.1f} requests per Monday**.

| Question | Model-based 95% interval | What it includes |
| --- | --- | --- |
| What is the underlying mean per Monday? | {monday.rate_low:.1f}–{monday.rate_high:.1f} requests | Posterior uncertainty about the mean: a **credible interval**. |
| How many requests might a new Monday have? | {int(monday.predictive_low)}–{int(monday.predictive_high)} requests | Uncertainty about the mean plus daily variation: a **posterior predictive interval**. |

The second range is wider because individual days vary around the mean.
Both rely on the model’s assumptions; the poor coverage above shows why they
cannot yet be trusted for planning. **Estimating an average precisely does not
make a busy day predictable.**

</details>

On the same October–December test, the **decision tree** misses by an average of
**{scores['Decision tree']:.1f} requests/day**, versus **{scores['Weekday average']:.1f}** for a simple weekday average
and **{scores['Gamma–Poisson']:.1f}** for the Bayesian mean. Lower is better.
Training excludes dates whose 30-day outcomes would not yet be known.
No model was tuned on these test results.

**The tree’s advantage does not hold in the 90-day check:** its average error rises
to {sensitivity_scores['Decision tree']:.1f}, versus {sensitivity_scores['Weekday average']:.1f} for the weekday average.
That check changes both the counted requests and the available training period.

This is a retrospective benchmark of selected reported activity, not a reliable
operational forecast. [See the prior–likelihood–posterior plot, predictive checks,
90-day sensitivity and reproducible methods](reports/iris_model_comparison.md).
'''
        args.readme_path.write_text(original[:original.index(start)+len(start)]+'\n\n'+body+'\n'+original[original.index(end):])
    print(metrics.round(2).to_string(index=False))
    print('Predictive coverage:',{h:r['coverage'] for h,r in results.items()})


if __name__=='__main__':
    main()
