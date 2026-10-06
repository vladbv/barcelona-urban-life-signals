# Reading Barcelona's reported civic activity

## Scope and headline cohort

The headline cohort contains records registered in 2025 and closed in 2025, as observed in this local export. Requests still open or closed in another year are absent. Late-year volumes and closure lags are therefore selected by the year-end cutoff; this is not a complete count of 2025 demand.

Source: [Open Data BCN — IRIS](https://opendata-ajuntament.barcelona.cat/data/en/dataset/iris), resource `efc9fd4d-a812-427c-846d-a086d22012a4`. Processed input: `data/processed/iris_2025_clean.csv` (283,911 records).

## A one-minute explanation

We are looking at 278,628 citizen reports registered and closed in 2025. Reporting follows a strong weekly rhythm, and cleaning and public-space maintenance make up 56.1% of this cohort. But 31.2% have no district, with coverage varying strongly by category and channel. Requests closed after year-end are absent, so late-year declines cannot be read as falling demand. Published request-type labels also change during the year. This is a useful description of reported activity; weather effects, causes, and service performance need further evidence.

## How to read the plots

Start with the bold takeaway below each plot. Then read how the chart works, what the numbers show, and why it matters. The last paragraph explains what we cannot conclude. This keeps evidence, explanation, and everyday human context together: ethos, logos, and pathos. Examples describe possible situations, not individual people identified in the data.

| Word                 | Plain meaning                                                                                                                                             |
| -------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Request / report     | One published IRIS entry. Several entries can concern the same issue.                                                                                     |
| Cohort               | The group we chose to study: here, requests registered and closed in 2025.                                                                                |
| Registration date    | When a request entered the system; the issue may have started earlier.                                                                                    |
| Recorded closure lag | Calendar days from registration to administrative closure. Closure does not prove the issue was resolved.                                                 |
| Median               | The middle value when values are put in order. At least half are at or below it.                                                                          |
| 95th percentile      | A value that at least 95 out of 100 observed values do not exceed; about 5 out of 100 are higher.                                                         |
| Share / percentage   | How many out of every 100 records in the stated group. A larger share need not mean more reports.                                                         |
| Correlation          | A score from −1 to +1 for how two quantities move together in a straight-line pattern. Near zero means little such pattern, not proof of no relationship. |

## 1. The rhythm of asking the city for help

![Daily observed requests and their trailing seven-day average across 2025.](figures/iris_daily_registration_volume.png)

**Takeaway: Report counts change through the year and repeatedly rise and fall within each week.**

*How to read it: The gold line counts records by registration date; the blue line averages seven complete calendar days so the broader movement is easier to see.*

The line rises and falls repeatedly through a year containing 278,628 reports. The median day has 784; the largest daily count is 1,572, on 3 July. Those sharp teeth invite us to look for a weekly reporting rhythm before searching for exceptional events.

Submitting a request is one way to bring an everyday concern to the council's attention. Seen together, these records show when that contact enters IRIS. The blue line helps us follow the changing pace without letting a single busy day dominate the story.

A registration date tells us when a request entered the system, not when the underlying issue began. Only requests closed in 2025 appear here, so the fall near December cannot by itself show that the city needed less help.

<details>
<summary>Inspect supporting data: iris_daily.csv (first 12 rows)</summary>

| registration_date   | requests | median_closure_lag_days | missing_district_percent | rolling_7_day | weekday   | month   |
| ------------------- | -------- | ----------------------- | ------------------------ | ------------- | --------- | ------- |
| 2025-01-01 00:00:00 | 254      | 7.0                     | 19.69                    |               | Wednesday | 2025-01 |
| 2025-01-02 00:00:00 | 575      | 6.0                     | 40.17                    |               | Thursday  | 2025-01 |
| 2025-01-03 00:00:00 | 528      | 6.0                     | 38.26                    |               | Friday    | 2025-01 |
| 2025-01-04 00:00:00 | 390      | 5.0                     | 17.95                    |               | Saturday  | 2025-01 |
| 2025-01-05 00:00:00 | 320      | 4.0                     | 25.0                     |               | Sunday    | 2025-01 |
| 2025-01-06 00:00:00 | 282      | 3.0                     | 29.08                    |               | Monday    | 2025-01 |
| 2025-01-07 00:00:00 | 726      | 2.0                     | 37.74                    | 439.29        | Tuesday   | 2025-01 |
| 2025-01-08 00:00:00 | 803      | 3.0                     | 37.11                    | 517.71        | Wednesday | 2025-01 |
| 2025-01-09 00:00:00 | 784      | 4.0                     | 39.16                    | 547.57        | Thursday  | 2025-01 |
| 2025-01-10 00:00:00 | 670      | 4.0                     | 32.99                    | 567.86        | Friday    | 2025-01 |
| 2025-01-11 00:00:00 | 449      | 4.0                     | 21.83                    | 576.29        | Saturday  | 2025-01 |
| 2025-01-12 00:00:00 | 380      | 3.0                     | 21.05                    | 584.86        | Sunday    | 2025-01 |

</details>

## 2. Reporting follows the working week

![Mean requests per calendar weekday, with weekends lower than Monday through Friday.](figures/iris_weekday_pattern.png)

**Takeaway: An average weekday has about 1.85 times the reports of an average weekend day.**

*How to read it: Each bar divides that weekday's total by the number of times it occurs in the year: 53 Wednesdays and 52 of each other weekday.*

Weekdays average 879 reports, compared with 474 at weekends: 1.85 times as many. Tuesday has the highest mean (912), and Sunday the lowest (463). The contrast is visible across the working week.

People fit contact with public services around their lives, and municipal channels have their own routines. Those are plausible contributors to this pattern. For someone planning a fair comparison, the practical lesson is to compare a Tuesday with similar weekdays before describing it as unusually busy.

The records do not measure opening hours, people's schedules, or all unreported concerns. A lower Sunday bar does not establish that fewer problems occurred that day, and this chart cannot separate the possible explanations.

<details>
<summary>Inspect supporting data: iris_weekday.csv (first 12 rows)</summary>

| weekday   | calendar_days | requests | mean_daily_requests |
| --------- | ------------- | -------- | ------------------- |
| Monday    | 52            | 46906    | 902.04              |
| Tuesday   | 52            | 47449    | 912.48              |
| Wednesday | 53            | 46554    | 878.38              |
| Thursday  | 52            | 45390    | 872.88              |
| Friday    | 52            | 43048    | 827.85              |
| Saturday  | 52            | 25223    | 485.06              |
| Sunday    | 52            | 24058    | 462.65              |

</details>

## 3. The calendar gives each day a context

![Month-by-weekday heatmap of mean daily reports; darker cells indicate higher counts.](figures/iris_month_weekday_heatmap.png)

**Takeaway: Compare similar days: a July Friday and a January Friday have different reporting levels in this file.**

*How to read it: Choose a month along the bottom and a weekday on the left. The number in their square is the average daily count for that combination; darker squares mean more reports.*

Fridays in July average 1,214 reports, compared with 640 in January. Weekend cells remain lighter than working-day cells across the year. Together, the two directions show why neither the weekday nor the month alone captures the whole reporting pattern.

For anyone trying to understand a busy day, its place in the calendar matters. Comparing similar weekdays in similar parts of the year gives us a more useful starting point for asking when reports tend to accumulate, without treating every peak as a special event.

Each square averages only four or five days. Holidays and a few unusual days can affect it. We have one year of selected completed records: the heatmap does not establish a repeating seasonal pattern, a tourism effect, or a weather effect.

<details>
<summary>Inspect supporting data: iris_daily.csv (first 12 rows)</summary>

| registration_date   | requests | median_closure_lag_days | missing_district_percent | rolling_7_day | weekday   | month   |
| ------------------- | -------- | ----------------------- | ------------------------ | ------------- | --------- | ------- |
| 2025-01-01 00:00:00 | 254      | 7.0                     | 19.69                    |               | Wednesday | 2025-01 |
| 2025-01-02 00:00:00 | 575      | 6.0                     | 40.17                    |               | Thursday  | 2025-01 |
| 2025-01-03 00:00:00 | 528      | 6.0                     | 38.26                    |               | Friday    | 2025-01 |
| 2025-01-04 00:00:00 | 390      | 5.0                     | 17.95                    |               | Saturday  | 2025-01 |
| 2025-01-05 00:00:00 | 320      | 4.0                     | 25.0                     |               | Sunday    | 2025-01 |
| 2025-01-06 00:00:00 | 282      | 3.0                     | 29.08                    |               | Monday    | 2025-01 |
| 2025-01-07 00:00:00 | 726      | 2.0                     | 37.74                    | 439.29        | Tuesday   | 2025-01 |
| 2025-01-08 00:00:00 | 803      | 3.0                     | 37.11                    | 517.71        | Wednesday | 2025-01 |
| 2025-01-09 00:00:00 | 784      | 4.0                     | 39.16                    | 547.57        | Thursday  | 2025-01 |
| 2025-01-10 00:00:00 | 670      | 4.0                     | 32.99                    | 567.86        | Friday    | 2025-01 |
| 2025-01-11 00:00:00 | 449      | 4.0                     | 21.83                    | 576.29        | Saturday  | 2025-01 |
| 2025-01-12 00:00:00 | 380      | 3.0                     | 21.05                    | 584.86        | Sunday    | 2025-01 |

</details>

## 4. December shows the edge of the dataset

![Monthly mean report counts and recorded closure lags, with an explanation of the December cutoff.](figures/iris_cohort_selection.png)

**Takeaway: Late-year requests that closed after 31 December are absent from this file.**

*How to read it: The upper panel shows mean daily reports by registration month. Below it are the median recorded closure lag and the 95th percentile, the point at or below which 95% of observed lags fall.*

The observed daily mean is highest in July, at 1,035; December's is 503. December also has a median lag of 2 days. These lower numbers are tempting to read as less pressure or faster service, but the file has a fixed boundary: every included request closed by 31 December.

Consider a request registered on 1 December. It can appear here with at most 30 days between registration and closure. A request registered on 31 December must close that same day. An unresolved concern can still matter to the person reporting it even when it falls outside this particular export.

This boundary can lower both the observed count and the observed lag late in the year; it does not tell us how much of the decline it explains. We need later closure records and comparable follow-up periods before judging changes in demand or closure speed.

<details>
<summary>Inspect supporting data: iris_monthly.csv (first 12 rows)</summary>

| month   | requests | calendar_days | mean_daily_requests | median_closure_lag_days | p95_closure_lag_days | closures_all_export | max_observable_lag_at_month_start | max_observable_lag_at_month_end |
| ------- | -------- | ------------- | ------------------- | ----------------------- | -------------------- | ------------------- | --------------------------------- | ------------------------------- |
| 2025-01 | 18491    | 31            | 596.48              | 3.0                     | 27.0                 | 19710               | 364                               | 334                             |
| 2025-02 | 18331    | 28            | 654.68              | 3.0                     | 28.0                 | 17823               | 333                               | 306                             |
| 2025-03 | 21569    | 31            | 695.77              | 3.0                     | 32.0                 | 20491               | 305                               | 275                             |
| 2025-04 | 21147    | 30            | 704.9               | 4.0                     | 34.0                 | 20862               | 274                               | 245                             |
| 2025-05 | 26164    | 31            | 844.0               | 3.0                     | 36.0                 | 24409               | 244                               | 214                             |
| 2025-06 | 29517    | 30            | 983.9               | 4.0                     | 35.0                 | 26788               | 213                               | 184                             |
| 2025-07 | 32076    | 31            | 1034.71             | 4.0                     | 43.0                 | 34079               | 183                               | 153                             |
| 2025-08 | 21470    | 31            | 692.58              | 4.0                     | 35.0                 | 21296               | 152                               | 122                             |
| 2025-09 | 25553    | 30            | 851.77              | 4.0                     | 33.0                 | 25714               | 121                               | 92                              |
| 2025-10 | 26546    | 31            | 856.32              | 4.0                     | 31.0                 | 27924               | 91                                | 61                              |
| 2025-11 | 22164    | 30            | 738.8               | 4.0                     | 26.0                 | 23099               | 60                                | 31                              |
| 2025-12 | 15600    | 31            | 503.23              | 2.0                     | 13.0                 | 21716               | 30                                | 0                               |

</details>

## 5. Much of the conversation concerns shared public space

![The largest request areas, led by cleaning and collection and public-space maintenance.](figures/iris_top_request_areas.png)

**Takeaway: Cleaning and public-space maintenance make up about 56 out of every 100 reports studied here.**

*How to read it: Bar length shows the number of reports in each displayed request area. The percentage beside it uses all headline records as its denominator, including areas outside the chart.*

Cleaning and collection (Recollida i neteja de l'espai urbà) account for 87,738 reports. Public-space maintenance (Manteniment de l'espai urbà) adds 68,491. Together that is 56.1% of the cohort: more than half of the records in this view concern these two areas.

Street cleanliness, pavements, and the upkeep of shared spaces are close to everyday city life. Their prominence makes this a concrete place to begin asking what citizens bring to the council's attention. It grounds the next analytical question in recognisable concerns about places people share.

Frequency is not a measure of severity. Several reports may refer to the same issue, and difficult or poorly reported problems may occupy small bars. The plot describes the published requests, not a ranking of everything that matters to Barcelona's residents.

<details>
<summary>Inspect supporting data: iris_areas.csv (first 12 rows)</summary>

| area                                    | requests | median_closure_lag_days | missing_district_rows | share_percent | missing_district_percent |
| --------------------------------------- | -------- | ----------------------- | --------------------- | ------------- | ------------------------ |
| Recollida i neteja de l'espai urbà      | 87738    | 3.0                     | 249                   | 31.49         | 0.28                     |
| Manteniment de l'espai urbà             | 68491    | 3.0                     | 142                   | 24.58         | 0.21                     |
| Portal de tràmits                       | 29259    | 2.0                     | 29259                 | 10.5          | 100.0                    |
| Informació  tràmits i atenció ciutadana | 17438    | 3.0                     | 17365                 | 6.26          | 99.58                    |
| Mobilitat                               | 13492    | 7.0                     | 1973                  | 4.84          | 14.62                    |
| Prevenció i seguretat                   | 12513    | 15.0                    | 782                   | 4.49          | 6.25                     |
| Gestions municipals                     | 10559    | 2.0                     | 10006                 | 3.79          | 94.76                    |
| Urbanisme                               | 7395     | 9.0                     | 4564                  | 2.65          | 61.72                    |
| Sanitat i salut pública                 | 6294     | 9.0                     | 192                   | 2.26          | 3.05                     |
| Serveis socials                         | 5916     | 14.0                    | 5916                  | 2.12          | 100.0                    |
| Cultura                                 | 5661     | 4.0                     | 5661                  | 2.03          | 100.0                    |
| Hisenda                                 | 3005     | 14.0                    | 3005                  | 1.08          | 100.0                    |

</details>

## 6. Many reports have no district on the map

![Counts by district, keeping the large missing-district group visible alongside named districts.](figures/iris_district_distribution.png)

**Takeaway: About 31 out of every 100 reports have no district, so a district-only view leaves many reports out.**

*How to read it: Each bar counts records assigned to a district; the '(missing)' bar counts records without a published district. Percentages refer to the entire headline cohort.*

86,953 reports, or 31.2%, have no district. Among named districts, Eixample has the largest count (33,514). Keeping the missing group in view makes the coverage gap visible before any geographic comparison.

A map can feel like a complete picture of a city. Here, drawing only the records we can place would leave nearly one third of the selected reports outside that picture. Keeping them visible helps us remember that a request can be relevant even when it cannot be assigned to a district.

A higher district count does not establish greater need, more problems per resident, or worse service. Districts differ in population, activity, and reporting habits, and none of those differences has been adjusted for here. Missing district also need not mean the publisher failed to locate a place-specific issue.

<details>
<summary>Inspect supporting data: iris_districts.csv (first 12 rows)</summary>

| district            | requests | median_closure_lag_days | missing_district_rows | share_percent | missing_district_percent |
| ------------------- | -------- | ----------------------- | --------------------- | ------------- | ------------------------ |
| (missing)           | 86953    | 3.0                     | 86953                 | 31.21         | 100.0                    |
| Eixample            | 33514    | 3.0                     | 0                     | 12.03         | 0.0                      |
| Sant Martí          | 31580    | 3.0                     | 0                     | 11.33         | 0.0                      |
| Sants-Montjuïc      | 21311    | 5.0                     | 0                     | 7.65          | 0.0                      |
| Horta-Guinardó      | 19535    | 4.0                     | 0                     | 7.01          | 0.0                      |
| Ciutat Vella        | 19397    | 4.0                     | 0                     | 6.96          | 0.0                      |
| Nou Barris          | 16656    | 4.0                     | 0                     | 5.98          | 0.0                      |
| Sant Andreu         | 15862    | 3.0                     | 0                     | 5.69          | 0.0                      |
| Gràcia              | 14572    | 4.0                     | 0                     | 5.23          | 0.0                      |
| Sarrià-Sant Gervasi | 12467    | 5.0                     | 0                     | 4.47          | 0.0                      |
| Les Corts           | 6781     | 5.0                     | 0                     | 2.43          | 0.0                      |

</details>

## 7. Geography is missing for different kinds of requests

![Percentage of records missing district in the ten largest request areas; coverage differs sharply by area.](figures/iris_geography_coverage.png)

**Takeaway: Removing reports without a district also changes which kinds of concerns we see.**

*How to read it: For each of the ten largest areas, the bar is the percentage of its records without a district. A longer bar means less geographic information, not more requests.*

Only 0.28% of cleaning records and 0.21% of maintenance records lack a district. For the administrative portal (Portal de tràmits), the missing share is 100%. The gap is strongly associated with the kind of request.

A damaged pavement has a physical location; a question about an online procedure may not. That difference is one plausible explanation for the contrast. If we keep only records with a district, we consequently hear much more about physical public space and much less about administrative services.

The file does not establish why any individual location is absent. We should neither invent districts to fill the gaps nor assume that records with a district represent the rest. Geographic filtering changes the question the analysis can answer.

<details>
<summary>Inspect supporting data: iris_areas.csv (first 12 rows)</summary>

| area                                    | requests | median_closure_lag_days | missing_district_rows | share_percent | missing_district_percent |
| --------------------------------------- | -------- | ----------------------- | --------------------- | ------------- | ------------------------ |
| Recollida i neteja de l'espai urbà      | 87738    | 3.0                     | 249                   | 31.49         | 0.28                     |
| Manteniment de l'espai urbà             | 68491    | 3.0                     | 142                   | 24.58         | 0.21                     |
| Portal de tràmits                       | 29259    | 2.0                     | 29259                 | 10.5          | 100.0                    |
| Informació  tràmits i atenció ciutadana | 17438    | 3.0                     | 17365                 | 6.26          | 99.58                    |
| Mobilitat                               | 13492    | 7.0                     | 1973                  | 4.84          | 14.62                    |
| Prevenció i seguretat                   | 12513    | 15.0                    | 782                   | 4.49          | 6.25                     |
| Gestions municipals                     | 10559    | 2.0                     | 10006                 | 3.79          | 94.76                    |
| Urbanisme                               | 7395     | 9.0                     | 4564                  | 2.65          | 61.72                    |
| Sanitat i salut pública                 | 6294     | 9.0                     | 192                   | 2.26          | 3.05                     |
| Serveis socials                         | 5916     | 14.0                    | 5916                  | 2.12          | 100.0                    |
| Cultura                                 | 5661     | 4.0                     | 5661                  | 2.03          | 100.0                    |
| Hisenda                                 | 3005     | 14.0                    | 3005                  | 1.08          | 100.0                    |

</details>

## 8. Districts differ in the mix of requests we can place

![Request-area shares within each known district, including all smaller areas in Other / missing.](figures/iris_district_area_mix_heatmap.png)

**Takeaway: Districts differ in the mix of reports received; these percentages do not rank districts from best to worst.**

*How to read it: Read across a district's row. Its percentages describe how that district's observed reports are divided among request areas; each row totals 100% before rounding.*

In Ciutat Vella, cleaning accounts for 58.7% of located reports and maintenance for 20.5%. In Horta-Guinardó, the corresponding shares are 35.6% and 47.0%. The balance of these two large categories is visibly different.

This invites a more specific local conversation: what kinds of concerns are reaching the council from each district? Looking at composition helps us see differences that a single citywide total would hide, while avoiding the assumption that every district's reported needs look alike.

A larger share of cleaning reports does not establish dirtier streets. A share can rise because other types of requests fall, and this chart excludes records with no district. It contains no adjustment for residents, visitors, or willingness and ability to report.

<details>
<summary>Inspect supporting data: iris_district_area_shares.csv (first 12 rows)</summary>

| district            | Recollida i neteja de l'espai urbà | Manteniment de l'espai urbà | Prevenció i seguretat | Mobilitat | Sanitat i salut pública | Urbanisme | Medi ambient | Transports públics | Other / missing |
| ------------------- | ---------------------------------- | --------------------------- | --------------------- | --------- | ----------------------- | --------- | ------------ | ------------------ | --------------- |
| Eixample            | 57.4                               | 24.52                       | 6.87                  | 6.07      | 1.89                    | 1.41      | 0.79         | 0.51               | 0.53            |
| Sant Martí          | 46.68                              | 35.93                       | 5.72                  | 5.16      | 3.68                    | 1.13      | 1.1          | 0.3                | 0.31            |
| Sants-Montjuïc      | 40.68                              | 38.42                       | 7.07                  | 6.63      | 3.36                    | 1.63      | 1.16         | 0.35               | 0.7             |
| Horta-Guinardó      | 35.6                               | 46.99                       | 4.64                  | 6.01      | 3.46                    | 1.3       | 1.16         | 0.5                | 0.35            |
| Ciutat Vella        | 58.7                               | 20.5                        | 8.88                  | 6.92      | 1.71                    | 1.62      | 1.05         | 0.24               | 0.38            |
| Nou Barris          | 36.59                              | 46.15                       | 5.07                  | 4.7       | 4.57                    | 1.16      | 0.98         | 0.29               | 0.49            |
| Sant Andreu         | 46.28                              | 36.6                        | 4.74                  | 5.32      | 3.61                    | 1.78      | 0.88         | 0.44               | 0.35            |
| Gràcia              | 45.33                              | 35.2                        | 6.0                   | 6.91      | 2.94                    | 1.72      | 0.88         | 0.58               | 0.45            |
| Sarrià-Sant Gervasi | 31.64                              | 46.87                       | 5.41                  | 7.46      | 4.36                    | 1.95      | 0.97         | 0.5                | 0.83            |
| Les Corts           | 37.1                               | 43.92                       | 5.06                  | 5.35      | 4.11                    | 1.73      | 1.61         | 0.46               | 0.66            |

</details>

## 9. The route into the system shapes what becomes visible

![Reporting-channel shares within request areas, with mobile prominent for cleaning and web for the administrative portal.](figures/iris_support_mix_by_area.png)

**Takeaway: Street-related reports and administrative questions often reach the council through different channels.**

*How to read it: Each horizontal bar represents all reports in one request area. Read the English labels first; the original published labels appear underneath in parentheses. Its coloured segments show reporting-channel shares; Other / missing preserves the channels outside the five displayed leaders. These are display translations, not merged categories.*

Mobile (MÒBIL) accounts for 60.7% of cleaning reports and 54.3% of maintenance reports. Web accounts for 96.9% of administrative portal requests. Different categories reach IRIS through markedly different routes.

Someone noticing an issue on a street and someone trying to complete an online procedure may approach the council differently. The chart makes that a useful question about access and reporting context. Understanding public concerns also requires understanding the routes by which those concerns become records.

These records do not identify who could not use a channel or why a channel was chosen. Differences may reflect request mix, available services, or administrative routing. They do not establish digital exclusion, citizen preferences, or a causal effect of channel on closure speed.

<details>
<summary>Inspect supporting data: iris_area_channel_shares.csv (first 12 rows)</summary>

| area                                    | MÒBIL | WEB   | TELÈFON | RECLAMACIÓ INTERNA | INSTÀNCIA TELEMÀTICA | Other / missing |
| --------------------------------------- | ----- | ----- | ------- | ------------------ | -------------------- | --------------- |
| Recollida i neteja de l'espai urbà      | 60.65 | 9.21  | 27.37   | 1.88               | 0.65                 | 0.25            |
| Manteniment de l'espai urbà             | 54.3  | 13.58 | 25.86   | 3.76               | 1.52                 | 0.97            |
| Portal de tràmits                       | 0.03  | 96.89 | 1.06    | 1.89               | 0.06                 | 0.07            |
| Informació  tràmits i atenció ciutadana | 1.1   | 51.92 | 36.97   | 3.61               | 0.68                 | 5.73            |
| Mobilitat                               | 45.73 | 27.09 | 16.68   | 4.55               | 4.05                 | 1.9             |
| Prevenció i seguretat                   | 6.88  | 43.99 | 22.54   | 8.29               | 14.37                | 3.92            |
| Gestions municipals                     | 0.09  | 6.97  | 89.91   | 2.98               | 0.01                 | 0.03            |
| Urbanisme                               | 8.33  | 59.86 | 18.65   | 10.45              | 1.85                 | 0.85            |

</details>

## 10. A typical closure time leaves a long tail out of view

![Counts in recorded closure-lag groups, retaining lags above 60 days in a separate final group.](figures/iris_closure_lag_histogram.png)

**Takeaway: The middle recorded closure time is 3 days, but 3,779 requests took more than 60 days to close.**

*How to read it: Bars count records in labelled calendar-day ranges, which have unequal widths. The final >60 bar contains every longer lag; its height is a count, not a rate per day.*

The median recorded lag is 3 days: at least half the selected records close within that interval. The 95th percentile is 32 days, and 3,779 records (1.4%) take more than 60 days. The maximum in this 2025-registration cohort is 286 days.

Three days is a useful description of the middle of this distribution, but it says little about the people whose requests remain in the administrative process much longer. Showing the tail keeps those less typical cases in the conversation instead of allowing one reassuring central number to stand for everyone.

A recorded closure is not proof that the person considered the issue resolved. Still-open requests are absent, and late-year registrations have less time to contribute long lags. The full export's longer maximum of 580 days includes earlier registrations and belongs to a different comparison.

<details>
<summary>Inspect supporting data: iris_closure_lag.csv (first 12 rows)</summary>

| lag_days | requests |
| -------- | -------- |
| 0        | 35343    |
| 1–3      | 104298   |
| 4–7      | 54608    |
| 8–14     | 35474    |
| 15–30    | 33845    |
| 31–60    | 11281    |
| >60      | 3779     |

</details>

## 11. Different requests have different closure timelines

![Median recorded closure lag by leading request area, with dot size and labels showing report counts.](figures/iris_area_volume_vs_lag.png)

**Takeaway: A single citywide closure-time figure cannot describe every kind of request fairly.**

*How to read it: A dot farther to the right means a longer median lag. Dot size and the adjacent number show report volume; the chart covers the twelve largest request areas.*

Cleaning has a median recorded lag of 3 days, and maintenance 3 days. Mobility (Mobilitat) has a median of 7 days, and prevention and safety (Prevenció i seguretat) 15 days. The categories with the largest volumes are not automatically those with the longest medians.

A question about a procedure and a report needing investigation need not follow the same administrative path. Looking at them separately makes the citywide median more understandable and gives us a fairer starting point for asking which processes might need closer study.

This is not a league table of good and bad service. The records do not make complexity, urgency, staffing, or the meaning of closure comparable across areas. The plot supports a question about differences in process; it does not identify their cause.

<details>
<summary>Inspect supporting data: iris_areas.csv (first 12 rows)</summary>

| area                                    | requests | median_closure_lag_days | missing_district_rows | share_percent | missing_district_percent |
| --------------------------------------- | -------- | ----------------------- | --------------------- | ------------- | ------------------------ |
| Recollida i neteja de l'espai urbà      | 87738    | 3.0                     | 249                   | 31.49         | 0.28                     |
| Manteniment de l'espai urbà             | 68491    | 3.0                     | 142                   | 24.58         | 0.21                     |
| Portal de tràmits                       | 29259    | 2.0                     | 29259                 | 10.5          | 100.0                    |
| Informació  tràmits i atenció ciutadana | 17438    | 3.0                     | 17365                 | 6.26          | 99.58                    |
| Mobilitat                               | 13492    | 7.0                     | 1973                  | 4.84          | 14.62                    |
| Prevenció i seguretat                   | 12513    | 15.0                    | 782                   | 4.49          | 6.25                     |
| Gestions municipals                     | 10559    | 2.0                     | 10006                 | 3.79          | 94.76                    |
| Urbanisme                               | 7395     | 9.0                     | 4564                  | 2.65          | 61.72                    |
| Sanitat i salut pública                 | 6294     | 9.0                     | 192                   | 2.26          | 3.05                     |
| Serveis socials                         | 5916     | 14.0                    | 5916                  | 2.12          | 100.0                    |
| Cultura                                 | 5661     | 4.0                     | 5661                  | 2.03          | 100.0                    |
| Hisenda                                 | 3005     | 14.0                    | 3005                  | 1.08          | 100.0                    |

</details>

## 12. Busy days do not tell the whole story of closure lag

![Daily observed report counts against median closure lag, coloured by the share missing district.](figures/iris_daily_volume_vs_closure_lag.png)

**Takeaway: Knowing how many reports arrived on a day tells us little about their typical recorded closure time in this comparison.**

*How to read it: Each dot is a registration day: left to right is its report count, and bottom to top is the median eventual recorded lag of those requests. Colour shows that day's percentage of records missing district.*

Across 365 observed days, the correlation is 0.11. This measure describes how consistently the two quantities move together in a straight-line pattern. A value close to zero, as here, indicates little such alignment; the dots do not form a clear rising line.

It is understandable to wonder whether more incoming requests mean longer waits. In this view, daily volume alone gives only a weak guide to the median lag. That directs attention to more specific questions about the kinds of requests received and the processes they enter.

The vertical axis is not how long that day's workload took to clear, and the plot does not measure backlog or staffing. Daily medians can hide long individual lags. Calendar effects, request mix, and the closure-year cutoff remain unadjusted, so a weak correlation cannot prove that workload has no effect.

<details>
<summary>Inspect supporting data: iris_daily.csv (first 12 rows)</summary>

| registration_date   | requests | median_closure_lag_days | missing_district_percent | rolling_7_day | weekday   | month   |
| ------------------- | -------- | ----------------------- | ------------------------ | ------------- | --------- | ------- |
| 2025-01-01 00:00:00 | 254      | 7.0                     | 19.69                    |               | Wednesday | 2025-01 |
| 2025-01-02 00:00:00 | 575      | 6.0                     | 40.17                    |               | Thursday  | 2025-01 |
| 2025-01-03 00:00:00 | 528      | 6.0                     | 38.26                    |               | Friday    | 2025-01 |
| 2025-01-04 00:00:00 | 390      | 5.0                     | 17.95                    |               | Saturday  | 2025-01 |
| 2025-01-05 00:00:00 | 320      | 4.0                     | 25.0                     |               | Sunday    | 2025-01 |
| 2025-01-06 00:00:00 | 282      | 3.0                     | 29.08                    |               | Monday    | 2025-01 |
| 2025-01-07 00:00:00 | 726      | 2.0                     | 37.74                    | 439.29        | Tuesday   | 2025-01 |
| 2025-01-08 00:00:00 | 803      | 3.0                     | 37.11                    | 517.71        | Wednesday | 2025-01 |
| 2025-01-09 00:00:00 | 784      | 4.0                     | 39.16                    | 547.57        | Thursday  | 2025-01 |
| 2025-01-10 00:00:00 | 670      | 4.0                     | 32.99                    | 567.86        | Friday    | 2025-01 |
| 2025-01-11 00:00:00 | 449      | 4.0                     | 21.83                    | 576.29        | Saturday  | 2025-01 |
| 2025-01-12 00:00:00 | 380      | 3.0                     | 21.05                    | 584.86        | Sunday    | 2025-01 |

</details>

## 13. The labels change, so the story needs a pause

![Monthly shares of unmerged source request-type labels, showing a transition from Catalan to English labels late in 2025.](figures/iris_request_type_labels.png)

**Takeaway: A change in published labels can look like a change in city problems unless we check the definitions.**

*How to read it: Rows are request-type labels exactly as published; columns are registration months. Each cell is that label's share of the month's records. A <1% label indicates a small nonzero share.*

October contains 0 records labelled INCIDENCIA and 17,071 labelled ISSUE. Other apparent Catalan/English counterparts shift as well, and October–December uses the English labels. The timing suggests a change in publication or classification, although this file does not explain it.

Without checking the labels, we could tell a dramatic story about one type of problem disappearing and another surging. Looking closely protects the people and services represented here from a conclusion the records cannot support. Sometimes the most useful finding is that a comparison needs more work.

We preserve both labels and do not merge apparent translations without a documented mapping. They do not identify the language used by citizens. Before using request-type trends to describe changes in city life, we need the publisher's explanation and a check that the categories remained comparable.

<details>
<summary>Inspect supporting data: iris_request_type_monthly.csv (first 12 rows)</summary>

| month   | AGRAIMENT | COMPLAINT | CONSULTA | GRATITUDE | INCIDENCIA | ISSUE | PETICIO DE SERVEI | QUEIXA | QUERY | SERVICE REQUEST | SUGGERIMENT | SUGGESTION |
| ------- | --------- | --------- | -------- | --------- | ---------- | ----- | ----------------- | ------ | ----- | --------------- | ----------- | ---------- |
| 2025-01 | 39        | 1         | 3530     | 0         | 10779      | 2     | 1010              | 2256   | 0     | 0               | 874         | 0          |
| 2025-02 | 39        | 0         | 3593     | 0         | 10090      | 2     | 1019              | 2372   | 0     | 0               | 1216        | 0          |
| 2025-03 | 44        | 15        | 4780     | 0         | 11398      | 7     | 974               | 2662   | 0     | 0               | 1687        | 2          |
| 2025-04 | 49        | 13        | 5133     | 0         | 10888      | 6     | 947               | 2478   | 0     | 0               | 1633        | 0          |
| 2025-05 | 52        | 35        | 5109     | 0         | 14635      | 28    | 1205              | 2966   | 3     | 0               | 2126        | 5          |
| 2025-06 | 43        | 65        | 3390     | 0         | 18756      | 35    | 1351              | 3940   | 7     | 1               | 1913        | 16         |
| 2025-07 | 42        | 239       | 3673     | 0         | 19973      | 100   | 1413              | 4418   | 39    | 1               | 2139        | 39         |
| 2025-08 | 32        | 313       | 2152     | 2         | 13577      | 192   | 1242              | 2547   | 67    | 4               | 1227        | 115        |
| 2025-09 | 28        | 1499      | 2496     | 9         | 11917      | 3848  | 1076              | 1778   | 694   | 180             | 1192        | 836        |
| 2025-10 | 0         | 3272      | 0        | 61        | 0          | 17071 | 0                 | 0      | 2919  | 1249            | 0           | 1974       |
| 2025-11 | 0         | 2720      | 0        | 46        | 0          | 13859 | 0                 | 0      | 2851  | 1146            | 0           | 1542       |
| 2025-12 | 0         | 1408      | 0        | 21        | 0          | 10197 | 0                 | 0      | 2185  | 825             | 0           | 964        |

</details>

## Reproducible methods

- Remove exact duplicate raw rows only; preserve observed category labels and missing geography. Raw downloads remain unchanged.
- Headline cohort: registration_date in 2025 within the inspected export whose closure_date is in 2025. Older registrations are retained in the processed file.
- Daily counts use all 365 calendar days. Weekday means divide by calendar exposure (including zero-record days); the trailing average requires seven complete days.
- District and channel compositions retain every record in their displayed group, using Other / missing for omitted categories. District composition excludes missing districts explicitly.
- Lags are calendar-day differences between published dates, not working days or verified resolution times. The histogram has unequal-width groups and an explicit >60-day group.
- Scatter plots include every day with defined lag; Pearson correlation is descriptive only. No minimum-volume threshold or statistical significance claim is used.
- Source labels remain in Catalan/English for traceability. Descriptions translate the broad meaning; they do not replace the source categories.
- The monthly table also includes closures_all_export, which counts all deduplicated closures including earlier registrations. It uses a different cohort from the headline registration counts.

## What comes next

Before weather integration, inspect adjacent closure-year resources and document a common observation window. Validate request-type label mappings against publisher metadata. Then define a specific weather question and an appropriate station/time resolution. No weather effect, recurring seasonality, causal claim, or forecast is established by this report.

## Data and provenance

Aggregate tables: `data/processed/summaries`. Standalone HTML: `reports/iris_exploration.html`. Input fingerprints and generation rules: `reports/iris_analysis_manifest.json`.

Processed SHA-256: `c8330100f876342f10ec36f83c2e4b1e12e26df27dd4ef2b4643a44956d784fa`.
