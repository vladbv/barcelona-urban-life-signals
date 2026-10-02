# Category and observation decisions

Decision date: 2026-09-27. Scope: the inspected local 2025 IRIS export.

## Preserve published request types

Do not merge `INCIDENCIA` with `ISSUE`, or other apparent translations, at this
stage. Keep `request_type` exactly as published. These labels show a strong
change over time: in the registered-and-closed-in-2025 cohort, October has
0 `INCIDENCIA` and 17,071 `ISSUE` records. October–December contains only the
English request-type labels, while earlier months predominantly contain the
Catalan labels.

This pattern is consistent with a publication/classification change, but the
file does not establish its cause or certify an exact crosswalk. It also does
not identify the language used by the reporting citizen. Unmerged request-type
trends must not be presented as changing incidence of a type of problem.

The generated `iris_request_type_monthly.csv` table and
`figures/iris_request_type_labels.png` make this visible. For current descriptive
comparisons, retain the observed `area` categories and explain their meaning in
the report. Before using a request-type mapping, validate it against publisher
documentation and inspect consistency across `AREA`, `ELEMENT`, and `DETALL`.
Preserve the original label even if a future additional grouped field is added.

## Keep reporting channels as descriptive groups

Channel is useful for describing how records appear, but it is not yet a
modelling feature. Missing district differs sharply by channel and request area;
a channel association can reflect request composition and administrative
routing. A modelling decision needs a specific outcome, a defined observation
window, and a review of whether channel information is available at that point.

## Use complete composition denominators

Charts showing only the leading areas or channels retain remaining categories
as `Other / missing`. Each percentage uses all records in the displayed row's
district or request area. District composition excludes missing district
explicitly; the district distribution and coverage chart include that group.

These are shares of reports, not population-adjusted rates. No population or
footfall denominator has been introduced, and no geography is imputed.

## Treat the export as selected by closure year

All observed closure dates are in 2025. Of 283,911 deduplicated records, 5,283
were registered before 2025. The headline cohort comprises the remaining
278,628 records registered and closed in 2025. Counts from the raw profile
include duplicates; the descriptive report and local viewer use deduplicated
records. The raw count of earlier registrations is 5,284, hence its difference
from the processed cohort count.

Requests still open or closed in another year are absent. A December 1
registration can contribute at most 30 days of lag; a December 31 registration
can contribute only zero days. Lower late-year counts or shorter lags therefore
cannot establish lower demand or improved service. The size of the excluded
cohort is unknown from this export.

The 2025 registration cohort's maximum lag is 286 days. The full export's
580-day maximum includes older registrations. These must not be interchanged.
Recorded closure is an administrative timestamp, not verified resolution.

## Calendar and relationship summaries

Count every calendar day in the selected interval, including days with no
observed records. Zero means no rows in this export, not no real-world issues.
Keep lag and geographic percentages undefined on days with zero records.
Use a trailing seven-calendar-day average only after seven days are available.
Weekday means divide by the number of that weekday in the selected interval.

Use every day with a defined median lag in the descriptive volume/lag scatter;
do not introduce an arbitrary volume threshold. Report correlation only with
at least three such days and variation in both quantities. This is an
unadjusted association, not an inferential or causal estimate.

## Gate before weather analysis

Inspect adjacent closure-year exports to understand how later closures change
registration coverage. Establish common follow-up windows and label stability
before joining weather. Additional years alone do not prove completeness:
unresolved requests may still be absent. A single closure-selected year cannot
establish recurring seasonality or a weather effect.


## Follow-up evidence (2026-10-02)

The adjacent export has now been inspected. It adds 6,419 registrations from
2025, including 5,331 in December, and contains closures through 2026-03-31.
See [the observation-window audit](iris_observation_windows.md) for the
30-day and 90-day definitions and their limits.

The publisher catalog defines TIPUS as a type of entry without listing a value
crosswalk. The 2026 source introduces `INCIDÈNCIA` alongside a broader return
to Catalan labels. Exact comparisons also find two area labels, 28 element
labels, and 135 detail labels not present in the preserved 2025 export.
No automatic merging is justified. Shared area names allow a narrowly stated
comparison but do not establish unchanged classification practice.
