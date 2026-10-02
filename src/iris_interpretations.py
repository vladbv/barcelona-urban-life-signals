"""One evidence-based, human-readable interpretation per plot of the inspected snapshot.

Ethos: disclose the source and limits. Logos: explain the encoding and numbers.
Pathos: make the civic stakes concrete without inventing experiences or causes.
The same passages appear in the README, Markdown guide, and offline report.
"""

from __future__ import annotations

import pandas as pd

from src.iris_signals import MISSING, registration_cohort, volume_lag_correlation

READING_APPROACH = (
    "Start with the bold takeaway below each plot. Then read how the chart works, "
    "what the numbers show, and why it matters. The last paragraph explains what "
    "we cannot conclude. This keeps evidence, explanation, and everyday human "
    "context together: ethos, logos, and pathos. Examples describe possible "
    "situations, not individual people identified in the data."
)

READING_GLOSSARY = [
    ("Request / report", "One published IRIS entry. Several entries can concern the same issue."),
    ("Cohort", "The group we chose to study: here, requests registered and closed in 2025."),
    ("Registration date", "When a request entered the system; the issue may have started earlier."),
    ("Recorded closure lag", "Calendar days from registration to administrative closure. Closure does not prove the issue was resolved."),
    ("Median", "The middle value when values are put in order. At least half are at or below it."),
    ("95th percentile", "A value that at least 95 out of 100 observed values do not exceed; about 5 out of 100 are higher."),
    ("Share / percentage", "How many out of every 100 records in the stated group. A larger share need not mean more reports."),
    ("Correlation", "A score from −1 to +1 for how two quantities move together in a straight-line pattern. Near zero means little such pattern, not proof of no relationship."),
]


def plot_readings(frame: pd.DataFrame, tables: dict[str, pd.DataFrame]) -> list[dict]:
    """Read the known 2025 snapshot; all quoted quantities come from its tables."""
    cohort = registration_cohort(frame)
    daily = tables["daily"]
    weekday = tables["weekday"].set_index("weekday")
    monthly = tables["monthly"].set_index("month")
    areas = tables["areas"].set_index("area")
    districts = tables["districts"].set_index("district")
    district_mix = tables["district_area_shares"].set_index("district")
    channel_mix = tables["area_channel_shares"].set_index("area")
    types = tables["request_type_monthly"].set_index("month")
    cleaning = "Recollida i neteja de l'espai urbà"
    maintenance = "Manteniment de l'espai urbà"
    portal = "Portal de tràmits"
    safety = "Prevenció i seguretat"
    mobile = "MÒBIL"

    work = weekday.iloc[:5]
    weekend = weekday.iloc[5:]
    work_mean = work["requests"].sum() / work["calendar_days"].sum()
    weekend_mean = weekend["requests"].sum() / weekend["calendar_days"].sum()
    ratio = work_mean / weekend_mean if weekend_mean else None
    ratio_text = f"{ratio:.2f} times as many" if ratio is not None else "more"
    busiest_weekday = weekday["mean_daily_requests"].idxmax()
    quietest_weekday = weekday["mean_daily_requests"].idxmin()
    peak_day = daily.loc[daily["requests"].idxmax()]
    peak_month = monthly["mean_daily_requests"].idxmax()
    peak_name = pd.Timestamp(peak_month).strftime("%B")
    calendar = daily.pivot_table(index="weekday", columns="month", values="requests", aggfunc="mean")
    missing_count = int(cohort["district"].isna().sum())
    missing_pct = missing_count / len(cohort) * 100
    largest_district = districts.drop(index=MISSING, errors="ignore")["requests"].idxmax()
    public_space = areas.loc[[cleaning, maintenance]]
    lag = cohort["closure_lag_days"]
    over_sixty = int(lag.gt(60).sum())
    corr = volume_lag_correlation(daily)
    corr_text = f"{corr:.2f}" if corr is not None else "not estimable"

    stories = [
        {
            "title": "The rhythm of asking the city for help",
            "figures": ["daily"], "table": "daily",
            "alt": "Daily observed requests and their trailing seven-day average across 2025.",
            "how_to_read": "The gold line counts records by registration date; the blue line averages seven complete calendar days so the broader movement is easier to see.",
            "finding": (
                f"The line rises and falls repeatedly through a year containing {len(cohort):,} "
                f"reports. The median day has {daily['requests'].median():,.0f}; the largest daily "
                f"count is {peak_day['requests']:,}, on {peak_day['registration_date'].day} "
                f"{peak_day['registration_date'].strftime('%B')}. Those sharp teeth invite us "
                "to look for a weekly reporting rhythm before searching for exceptional events."
            ),
            "meaning": "Submitting a request is one way to bring an everyday concern to the council's attention. Seen together, these records show when that contact enters IRIS. The blue line helps us follow the changing pace without letting a single busy day dominate the story.",
            "limit": "A registration date tells us when a request entered the system, not when the underlying issue began. Only requests closed in 2025 appear here, so the fall near December cannot by itself show that the city needed less help.",
        },
        {
            "title": "Reporting follows the working week",
            "figures": ["weekday"], "table": "weekday",
            "alt": "Mean requests per calendar weekday, with weekends lower than Monday through Friday.",
            "how_to_read": "Each bar divides that weekday's total by the number of times it occurs in the year: 53 Wednesdays and 52 of each other weekday.",
            "finding": (
                f"Weekdays average {work_mean:,.0f} reports, compared with {weekend_mean:,.0f} "
                f"at weekends: {ratio_text}. {busiest_weekday} has the highest mean "
                f"({weekday.loc[busiest_weekday, 'mean_daily_requests']:,.0f}), and "
                f"{quietest_weekday} the lowest ({weekday.loc[quietest_weekday, 'mean_daily_requests']:,.0f}). "
                "The contrast is visible across the working week."
            ),
            "meaning": "People fit contact with public services around their lives, and municipal channels have their own routines. Those are plausible contributors to this pattern. For someone planning a fair comparison, the practical lesson is to compare a Tuesday with similar weekdays before describing it as unusually busy.",
            "limit": "The records do not measure opening hours, people's schedules, or all unreported concerns. A lower Sunday bar does not establish that fewer problems occurred that day, and this chart cannot separate the possible explanations.",
        },
        {
            "title": "The calendar gives each day a context",
            "figures": ["calendar"], "table": "daily",
            "alt": "Month-by-weekday heatmap of mean daily reports; darker cells indicate higher counts.",
            "how_to_read": "Choose a month along the bottom and a weekday on the left. The number in their square is the average daily count for that combination; darker squares mean more reports.",
            "finding": (
                f"Fridays in July average {calendar.loc['Friday', '2025-07']:,.0f} reports, "
                f"compared with {calendar.loc['Friday', '2025-01']:,.0f} in January. "
                "Weekend cells remain lighter than working-day cells across the year. "
                "Together, the two directions show why neither the weekday nor the month "
                "alone captures the whole reporting pattern."
            ),
            "meaning": "For anyone trying to understand a busy day, its place in the calendar matters. Comparing similar weekdays in similar parts of the year gives us a more useful starting point for asking when reports tend to accumulate, without treating every peak as a special event.",
            "limit": "Each square averages only four or five days. Holidays and a few unusual days can affect it. We have one year of selected completed records: the heatmap does not establish a repeating seasonal pattern, a tourism effect, or a weather effect.",
        },
        {
            "title": "December shows the edge of the dataset",
            "figures": ["selection"], "table": "monthly",
            "alt": "Monthly mean report counts and recorded closure lags, with an explanation of the December cutoff.",
            "how_to_read": "The upper panel shows mean daily reports by registration month. Below it are the median recorded closure lag and the 95th percentile, the point at or below which 95% of observed lags fall.",
            "finding": (
                f"The observed daily mean is highest in {peak_name}, at "
                f"{monthly.loc[peak_month, 'mean_daily_requests']:,.0f}; December's is "
                f"{monthly.loc['2025-12', 'mean_daily_requests']:,.0f}. December also has a "
                f"median lag of {monthly.loc['2025-12', 'median_closure_lag_days']:g} days. "
                "These lower numbers are tempting to read as less pressure or faster service, "
                "but the file has a fixed boundary: every included request closed by 31 December."
            ),
            "meaning": "Consider a request registered on 1 December. It can appear here with at most 30 days between registration and closure. A request registered on 31 December must close that same day. An unresolved concern can still matter to the person reporting it even when it falls outside this particular export.",
            "limit": "This boundary can lower both the observed count and the observed lag late in the year; it does not tell us how much of the decline it explains. We need later closure records and comparable follow-up periods before judging changes in demand or closure speed.",
        },
        {
            "title": "Much of the conversation concerns shared public space",
            "figures": ["areas"], "table": "areas",
            "alt": "The largest request areas, led by cleaning and collection and public-space maintenance.",
            "how_to_read": "Bar length shows the number of reports in each displayed request area. The percentage beside it uses all headline records as its denominator, including areas outside the chart.",
            "finding": (
                f"Cleaning and collection (Recollida i neteja de l'espai urbà) account for "
                f"{areas.loc[cleaning, 'requests']:,} reports. Public-space maintenance "
                f"(Manteniment de l'espai urbà) adds {areas.loc[maintenance, 'requests']:,}. "
                f"Together that is {public_space['share_percent'].sum():.1f}% of the cohort: "
                "more than half of the records in this view concern these two areas."
            ),
            "meaning": "Street cleanliness, pavements, and the upkeep of shared spaces are close to everyday city life. Their prominence makes this a concrete place to begin asking what citizens bring to the council's attention. It grounds the next analytical question in recognisable concerns about places people share.",
            "limit": "Frequency is not a measure of severity. Several reports may refer to the same issue, and difficult or poorly reported problems may occupy small bars. The plot describes the published requests, not a ranking of everything that matters to Barcelona's residents.",
        },
        {
            "title": "Many reports have no district on the map",
            "figures": ["districts"], "table": "districts",
            "alt": "Counts by district, keeping the large missing-district group visible alongside named districts.",
            "how_to_read": "Each bar counts records assigned to a district; the '(missing)' bar counts records without a published district. Percentages refer to the entire headline cohort.",
            "finding": (
                f"{missing_count:,} reports, or {missing_pct:.1f}%, have no district. "
                f"Among named districts, {largest_district} has the largest count "
                f"({districts.loc[largest_district, 'requests']:,}). Keeping the missing "
                "group in view makes the coverage gap visible before any geographic comparison."
            ),
            "meaning": "A map can feel like a complete picture of a city. Here, drawing only the records we can place would leave nearly one third of the selected reports outside that picture. Keeping them visible helps us remember that a request can be relevant even when it cannot be assigned to a district.",
            "limit": "A higher district count does not establish greater need, more problems per resident, or worse service. Districts differ in population, activity, and reporting habits, and none of those differences has been adjusted for here. Missing district also need not mean the publisher failed to locate a place-specific issue.",
        },
        {
            "title": "Geography is missing for different kinds of requests",
            "figures": ["missingness"], "table": "areas",
            "alt": "Percentage of records missing district in the ten largest request areas; coverage differs sharply by area.",
            "how_to_read": "For each of the ten largest areas, the bar is the percentage of its records without a district. A longer bar means less geographic information, not more requests.",
            "finding": (
                f"Only {areas.loc[cleaning, 'missing_district_percent']:.2f}% of cleaning "
                f"records and {areas.loc[maintenance, 'missing_district_percent']:.2f}% of "
                f"maintenance records lack a district. For the administrative portal "
                f"(Portal de tràmits), the missing share is {areas.loc[portal, 'missing_district_percent']:.0f}%. "
                "The gap is strongly associated with the kind of request."
            ),
            "meaning": "A damaged pavement has a physical location; a question about an online procedure may not. That difference is one plausible explanation for the contrast. If we keep only records with a district, we consequently hear much more about physical public space and much less about administrative services.",
            "limit": "The file does not establish why any individual location is absent. We should neither invent districts to fill the gaps nor assume that records with a district represent the rest. Geographic filtering changes the question the analysis can answer.",
        },
        {
            "title": "Districts differ in the mix of requests we can place",
            "figures": ["district_mix"], "table": "district_area_shares",
            "alt": "Request-area shares within each known district, including all smaller areas in Other / missing.",
            "how_to_read": "Read across a district's row. Its percentages describe how that district's observed reports are divided among request areas; each row totals 100% before rounding.",
            "finding": (
                f"In Ciutat Vella, cleaning accounts for {district_mix.loc['Ciutat Vella', cleaning]:.1f}% "
                f"of located reports and maintenance for {district_mix.loc['Ciutat Vella', maintenance]:.1f}%. "
                f"In Horta-Guinardó, the corresponding shares are "
                f"{district_mix.loc['Horta-Guinardó', cleaning]:.1f}% and "
                f"{district_mix.loc['Horta-Guinardó', maintenance]:.1f}%. "
                "The balance of these two large categories is visibly different."
            ),
            "meaning": "This invites a more specific local conversation: what kinds of concerns are reaching the council from each district? Looking at composition helps us see differences that a single citywide total would hide, while avoiding the assumption that every district's reported needs look alike.",
            "limit": "A larger share of cleaning reports does not establish dirtier streets. A share can rise because other types of requests fall, and this chart excludes records with no district. It contains no adjustment for residents, visitors, or willingness and ability to report.",
        },
        {
            "title": "The route into the system shapes what becomes visible",
            "figures": ["channels"], "table": "area_channel_shares",
            "alt": "Reporting-channel shares within request areas, with mobile prominent for cleaning and web for the administrative portal.",
            "how_to_read": "Each horizontal bar represents all reports in one request area. Its coloured segments show reporting-channel shares; Other / missing preserves the channels outside the five displayed leaders.",
            "finding": (
                f"Mobile (MÒBIL) accounts for {channel_mix.loc[cleaning, mobile]:.1f}% of "
                f"cleaning reports and {channel_mix.loc[maintenance, mobile]:.1f}% of "
                f"maintenance reports. Web accounts for {channel_mix.loc[portal, 'WEB']:.1f}% "
                "of administrative portal requests. Different categories reach IRIS "
                "through markedly different routes."
            ),
            "meaning": "Someone noticing an issue on a street and someone trying to complete an online procedure may approach the council differently. The chart makes that a useful question about access and reporting context. Understanding public concerns also requires understanding the routes by which those concerns become records.",
            "limit": "These records do not identify who could not use a channel or why a channel was chosen. Differences may reflect request mix, available services, or administrative routing. They do not establish digital exclusion, citizen preferences, or a causal effect of channel on closure speed.",
        },
        {
            "title": "A typical closure time leaves a long tail out of view",
            "figures": ["lag"], "table": "closure_lag",
            "alt": "Counts in recorded closure-lag groups, retaining lags above 60 days in a separate final group.",
            "how_to_read": "Bars count records in labelled calendar-day ranges, which have unequal widths. The final >60 bar contains every longer lag; its height is a count, not a rate per day.",
            "finding": (
                f"The median recorded lag is {lag.median():g} days: at least half the "
                f"selected records close within that interval. The 95th percentile is "
                f"{lag.quantile(.95):g} days, and {over_sixty:,} records "
                f"({over_sixty / len(cohort) * 100:.1f}%) take more than 60 days. "
                f"The maximum in this 2025-registration cohort is {lag.max():g} days."
            ),
            "meaning": "Three days is a useful description of the middle of this distribution, but it says little about the people whose requests remain in the administrative process much longer. Showing the tail keeps those less typical cases in the conversation instead of allowing one reassuring central number to stand for everyone.",
            "limit": "A recorded closure is not proof that the person considered the issue resolved. Still-open requests are absent, and late-year registrations have less time to contribute long lags. The full export's longer maximum of " + f"{frame['closure_lag_days'].max():g} days includes earlier registrations and belongs to a different comparison.",
        },
        {
            "title": "Different requests have different closure timelines",
            "figures": ["area_lag"], "table": "areas",
            "alt": "Median recorded closure lag by leading request area, with dot size and labels showing report counts.",
            "how_to_read": "A dot farther to the right means a longer median lag. Dot size and the adjacent number show report volume; the chart covers the twelve largest request areas.",
            "finding": (
                f"Cleaning has a median recorded lag of "
                f"{areas.loc[cleaning, 'median_closure_lag_days']:g} days, and maintenance "
                f"{areas.loc[maintenance, 'median_closure_lag_days']:g} days. Mobility "
                f"(Mobilitat) has a median of {areas.loc['Mobilitat', 'median_closure_lag_days']:g} "
                f"days, and prevention and safety (Prevenció i seguretat) "
                f"{areas.loc[safety, 'median_closure_lag_days']:g} days. "
                "The categories with the largest volumes are not automatically those with the longest medians."
            ),
            "meaning": "A question about a procedure and a report needing investigation need not follow the same administrative path. Looking at them separately makes the citywide median more understandable and gives us a fairer starting point for asking which processes might need closer study.",
            "limit": "This is not a league table of good and bad service. The records do not make complexity, urgency, staffing, or the meaning of closure comparable across areas. The plot supports a question about differences in process; it does not identify their cause.",
        },
        {
            "title": "Busy days do not tell the whole story of closure lag",
            "figures": ["scatter"], "table": "daily",
            "alt": "Daily observed report counts against median closure lag, coloured by the share missing district.",
            "how_to_read": "Each dot is a registration day: left to right is its report count, and bottom to top is the median eventual recorded lag of those requests. Colour shows that day's percentage of records missing district.",
            "finding": (
                f"Across {daily['median_closure_lag_days'].notna().sum()} observed days, "
                f"the correlation is {corr_text}. This measure describes how consistently "
                "the two quantities move together in a straight-line pattern. A value "
                "close to zero, as here, indicates little such alignment; the dots do "
                "not form a clear rising line."
            ),
            "meaning": "It is understandable to wonder whether more incoming requests mean longer waits. In this view, daily volume alone gives only a weak guide to the median lag. That directs attention to more specific questions about the kinds of requests received and the processes they enter.",
            "limit": "The vertical axis is not how long that day's workload took to clear, and the plot does not measure backlog or staffing. Daily medians can hide long individual lags. Calendar effects, request mix, and the closure-year cutoff remain unadjusted, so a weak correlation cannot prove that workload has no effect.",
        },
        {
            "title": "The labels change, so the story needs a pause",
            "figures": ["types"], "table": "request_type_monthly",
            "alt": "Monthly shares of unmerged source request-type labels, showing a transition from Catalan to English labels late in 2025.",
            "how_to_read": "Rows are request-type labels exactly as published; columns are registration months. Each cell is that label's share of the month's records. A <1% label indicates a small nonzero share.",
            "finding": (
                f"October contains {int(types.loc['2025-10', 'INCIDENCIA']):,} records "
                f"labelled INCIDENCIA and {int(types.loc['2025-10', 'ISSUE']):,} labelled ISSUE. "
                "Other apparent Catalan/English counterparts shift as well, and "
                "October–December uses the English labels. The timing suggests a "
                "change in publication or classification, although this file does not explain it."
            ),
            "meaning": "Without checking the labels, we could tell a dramatic story about one type of problem disappearing and another surging. Looking closely protects the people and services represented here from a conclusion the records cannot support. Sometimes the most useful finding is that a comparison needs more work.",
            "limit": "We preserve both labels and do not merge apparent translations without a documented mapping. They do not identify the language used by citizens. Before using request-type trends to describe changes in city life, we need the publisher's explanation and a check that the categories remained comparable.",
        },
    ]

    takeaways = {
        "daily": "Report counts change through the year and repeatedly rise and fall within each week.",
        "weekday": f"An average weekday has about {ratio:.2f} times the reports of an average weekend day." if ratio is not None else "Compare daily averages before comparing weekdays.",
        "calendar": "Compare similar days: a July Friday and a January Friday have different reporting levels in this file.",
        "selection": "Late-year requests that closed after 31 December are absent from this file.",
        "areas": f"Cleaning and public-space maintenance make up about {public_space['share_percent'].sum():.0f} out of every 100 reports studied here.",
        "districts": f"About {missing_pct:.0f} out of every 100 reports have no district, so a district-only view leaves many reports out.",
        "missingness": "Removing reports without a district also changes which kinds of concerns we see.",
        "district_mix": "Districts differ in the mix of reports received; these percentages do not rank districts from best to worst.",
        "channels": "Street-related reports and administrative questions often reach the council through different channels.",
        "lag": f"The middle recorded closure time is {lag.median():g} days, but {over_sixty:,} requests took more than 60 days to close.",
        "area_lag": "A single citywide closure-time figure cannot describe every kind of request fairly.",
        "scatter": "Knowing how many reports arrived on a day tells us little about their typical recorded closure time in this comparison.",
        "types": "A change in published labels can look like a change in city problems unless we check the definitions.",
    }
    for story in stories:
        story["takeaway"] = takeaways[story["figures"][0]]
    return stories
