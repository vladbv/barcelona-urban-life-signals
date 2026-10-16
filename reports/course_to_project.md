# From graduate training to a defensible city-data analysis

The project draws on my Master’s in Data Science, Statistics and Decision
Analysis. The practical question comes first: what can these records tell us
about reported needs, and which conclusions would the data fail to support?

## Course connections and current evidence

| Training | Connection to this project | Status |
| --- | --- | --- |
| Machine Learning: preprocessing, pipelines and evaluation | Reproducible preparation and validation are implemented. A future predictor would fit preprocessing on training data only and be evaluated on later dates. | Preparation implemented; model training and evaluation planned. |
| Data Mining: pattern discovery, clustering and anomaly detection | Current summaries expose weekday patterns, category changes and missing geography. Clustering or anomaly detection would require a defined question and validation; neither is currently implemented. | Descriptive exploration implemented. |
| Statistical Modelling: distributions, likelihood and estimation | Counts and elapsed days are different outcomes. Denominators, population selection and the meaning of a recorded closure are defined before choosing a distribution. | Data and outcome checks implemented; likelihood-based modelling planned. |
| Bayesian Learning: conjugacy, simulation and predictive distributions | A proposed count-model comparison would examine posterior uncertainty, prior sensitivity and predictive fit. | Proposed; no posterior estimates or Bayesian results published. |

My Bayesian Learning exercises in R cover inverse-transform sampling, rejection
sampling, importance sampling and Monte Carlo numerical error. This training
provides a foundation for checking simulations. Other relevant course concepts
include conjugate updating, posterior approximation and prediction. Coursework
and proposed methods are separate from this repository’s implemented results.

## One useful Bayesian question, after the observation and weather checks

How variable are daily counts of cleaning requests registered in 2025 and marked
closed within 30 days? Repeat the comparison with a 90-day definition. The target
is an observed, selected group of requests—not total demand or successful repairs.

A **Gamma–Poisson** model could be a transparent conjugate reference model for
comparable days: a Gamma prior for a Poisson rate gives a Gamma posterior.
It would not, by itself, account for weekday differences, changing rates or
serial dependence. Check those assumptions and whether variability exceeds the
Poisson model’s conditional mean before treating it as useful.

The proposed analysis would:

1. State the likelihood and justify a proper, weakly informative prior using
   plausible request counts; compare alternative prior choices.
2. Report posterior summaries and credible intervals for the modelled rate.
   These quantify uncertainty conditional on the model and selected records.
3. Use the posterior predictive distribution for new counts, incorporating both
   parameter uncertainty and variation in observations. Predictive intervals
   answer a different question from credible intervals for the rate.
4. Check simulated patterns against observations, compare with a simple calendar
   baseline and evaluate predictions on held-out later dates. A training request’s
   closure outcome must already be observable at the simulated prediction date.
5. If simulation is needed, assess Monte Carlo numerical error separately from
   uncertainty about city activity. Neither can repair missing source coverage.

This is a modelling proposal, not a change to the current descriptive milestone.
A more complex model earns its place only if it answers the question better.

## Statistical distinctions that matter

- **Proper is not the same as uninformative.** A Gamma prior with positive shape
  and rate is proper; how informative it is depends on its parameters and context.
- **Uniform is not assumption-free.** Dirichlet(1, …, 1) is uniform on the simplex
  in the usual probability coordinates. It is not a universally neutral prior;
  assess sensitivity rather than describing it as “prior ignorance”.
- **Observed and expected information differ.** Observed information is the
  negative log-likelihood Hessian and may depend on observed data. Jeffreys’ prior
  uses expected Fisher information, taking expectation under the model.
- **Approximation needs checking.** A normal approximation around a posterior
  mode can be misleading for skewed or boundary-constrained distributions.
  Conjugate calculations, a grid or simulation can provide checks when applicable.

See the [project plan](../PROJECT_PLAN.md), [implemented analysis](../src/iris_signals.py)
and [observation-window audit](iris_observation_windows.md) for the current evidence.
