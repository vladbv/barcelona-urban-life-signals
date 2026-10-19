# From graduate training to tested predictions

My Master’s in Data Science, Statistics and Decision Analysis informs a practical
question: can reported requests help us anticipate contact with the council?
Unreliable estimates could hide busy days. This project checks that risk before
suggesting an operational use.

## Four courses, inspectable evidence

| Training | Implemented work | What it demonstrates |
| --- | --- | --- |
| Machine Learning | A shallow decision tree using weekday and day of year; comparison with a weekday-average baseline on later dates, plus expanding-window checks in three earlier months. | Model fitting, explicit features, time-based cross-validation, MAE and RMSE. No tuning on the test quarter. |
| Data Mining | Duplicate and identifier checks, weekday patterns, topic summaries, missing geography and a closure-window audit. | Pattern discovery with attention to sample selection. No clustering or anomaly detector is claimed. |
| Statistical Modelling | A Poisson likelihood for daily observed counts, separate rates by weekday and variance-to-mean diagnostics. | Distributional assumptions must be checked against the variation in real data. |
| Bayesian Learning | Gamma–Poisson conjugate updating, posterior credible intervals, predictive simulation, prior sensitivity and posterior predictive checks. | Parameter uncertainty differs from uncertainty about a new day’s count. Simulation error is recorded separately. |

[Model implementation](../src/model_iris_counts.py) ·
[Results, plots and methods](iris_model_comparison.md) ·
[Observation audit](iris_observation_windows.md) · [Tests](../tests/).

## Prior → likelihood → posterior → prediction

The **prior** describes possible daily rates before using the training counts.
The **likelihood** measures how well a rate explains those counts under the
Poisson assumption. The **posterior** combines both. Drawing a rate from that
posterior, then a count from its Poisson distribution, gives a **posterior
predictive simulation** for a new day.

Here the prior is Gamma(shape=2, rate=0.01). For each weekday, observing a total
of *S* requests over *n* training days gives Gamma(2 + S, 0.01 + n).
This is an actual conjugate update, with seeded simulation used for intervals
and model checks. The proper prior is a broad illustrative assumption; it is
neither assumption-free nor elicited expert knowledge.

The result is instructive: the nominal 95% predictive intervals contain only
39% of later days in the 30-day analysis. Training observations also vary more
than replicated samples from the model. More precise estimation of a constant
rate does not repair a poor model of daily variability.

The tree reduces average error in that analysis, but loses to the simple
baseline in the 90-day check. That check changes both the outcome and available
training dates. It does not establish a universally better model.

The [earlier-month validation](iris_temporal_validation.md) checks whether that
advantage repeats: the tree beats the weekday average in only one of April,
June and August. This is why model assessment needs more than a single split.
The follow-up is retrospective and leaves the original test quarter separate.

## What these methods do not establish

The target is observed cleaning requests marked closed within a fixed period,
not all demand or successful repairs. Historical publication delays are unknown,
so this is a retrospective benchmark, not a production simulation.

The decision tree needs no activation function. Neural networks, clustering,
Jeffreys’ priors and posterior approximations are not implemented here; they
would need a question that justifies them. The coursework R exercises informed
the simulation checks but are not copied into the project.

Next modelling work should investigate changing rates and overdispersion using
validation periods within training data. The October–December test quarter has
now been seen and must not become a tuning target.
