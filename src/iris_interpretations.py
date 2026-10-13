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
    ("Request / report", "One entry sent to the council and published in IRIS: for example an incident report, complaint, inquiry or suggestion. Several entries can concern the same issue."),
    ("Cohort", "The group we chose to study: here, requests registered and closed in 2025."),
    ("Registration date", "When a request entered the system; the issue may have started earlier."),
    ("Time until marked closed (closure lag)", "Calendar days between a request entering IRIS and its recorded closing date. Marked closed is an administrative status; it does not prove the underlying issue was fixed."),
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
            "title": "When residents submit requests to the council",
            "figures": ["daily"], "table": "daily",
            "alt": "Daily observed requests and their trailing seven-day average across 2025.",
            "how_to_read": "The gold line counts records by registration date; the blue line averages seven complete calendar days so the broader movement is easier to see.",
            "finding": (
                f"The line rises and falls repeatedly through a year containing {len(cohort):,} "
                f"reports. The median day has {daily['requests'].median():,.0f}; the largest daily "
                f"count is {peak_day['requests']:,}, on {peak_day['registration_date'].day} "
                f"{peak_day['registration_date'].strftime('%B')}. The repeated rises and falls suggest "
                "checking weekday patterns before treating a busy day as an unusual event."
            ),
            "meaning": "Submitting a request is one way to bring an everyday concern to the council's attention. Seen together, these records show when that contact enters IRIS. The blue line helps us follow the changing pace without letting a single busy day dominate the story.",
            "limit": "A registration date tells us when a request entered the system, not when the underlying issue began. Only requests closed in 2025 appear here, so the fall near December cannot by itself show that the city needed less help.",
        },
        {
            "title": "More requests are registered on weekdays",
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
            "title": "How request counts vary by month and weekday",
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
            "title": "Why late-year requests are missing from this view",
            "figures": ["selection"], "table": "monthly",
            "alt": "Monthly mean report counts and recorded closure lags, with an explanation of the December cutoff.",
            "how_to_read": "The top panel shows the average number of requests registered per day in each month. The lower panel measures days until requests were marked closed: one line shows the middle time (median), and the other the time within which about 95 out of 100 requests were marked closed.",
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
            "title": "Cleaning and street maintenance account for most requests",
            "figures": ["areas"], "table": "areas",
            "alt": "The largest request areas, led by cleaning and collection and public-space maintenance.",
            "how_to_read": "Each bar shows how many requests concern a particular council service or topic. English labels appear first, followed by the published labels in parentheses. A label of 31.5% means about 32 of every 100 requests in the study; the percentages include categories not shown among these 12 bars.",
            "finding": (
                f"Cleaning and collection (Recollida i neteja de l'espai urbà) account for "
                f"{areas.loc[cleaning, 'requests']:,} reports. Public-space maintenance "
                f"(Manteniment de l'espai urbà) adds {areas.loc[maintenance, 'requests']:,}. "
                f"Together that is {public_space['share_percent'].sum():.1f}% of the requests studied: "
                "more than half of the records in this view concern these two areas."
            ),
            "meaning": "Each entry records contact with the council about a service or topic. Cleaning and maintenance concern places people use every day: pavements, streets and other public spaces. Their large share tells us that caring for those places is a major part of the contact recorded in this file. The other bars include inquiries and administrative matters as well as reports of problems.",
            "limit": "Frequency is not a measure of severity. Several reports may refer to the same issue, and difficult or poorly reported problems may occupy small bars. The plot describes the published requests, not a ranking of everything that matters to Barcelona's residents.",
        },
        {
            "title": "Almost one in three requests has no recorded district",
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
            "title": "Some request categories have much less location information",
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
            "title": "What types of requests are recorded in each district",
            "figures": ["district_mix"], "table": "district_area_shares",
            "alt": "Request-area shares within each known district, including all smaller areas in Other / missing.",
            "how_to_read": "Each row is a district, not an individual neighbourhood. Read across it as 100 requests assigned to that district: each cell shows how many out of those 100 fall into a request category. Darker means a larger share of reports, not worse living conditions. Each row totals 100% before rounding; English category labels appear above the original names.",
            "finding": (
                f"In Ciutat Vella, cleaning accounts for {district_mix.loc['Ciutat Vella', cleaning]:.1f}% "
                f"of located reports and maintenance for {district_mix.loc['Ciutat Vella', maintenance]:.1f}%. "
                f"In Horta-Guinardó, the corresponding shares are "
                f"{district_mix.loc['Horta-Guinardó', cleaning]:.1f}% and "
                f"{district_mix.loc['Horta-Guinardó', maintenance]:.1f}%. "
                "The balance of these two large categories is visibly different."
            ),
            "meaning": "This chart answers what people contact the council about in each district. That can help someone preparing a local discussion pay attention to the topics most often raised there. It does not answer which district is the best place to live, which has the cleanest streets, or which provides the best service.",
            "limit": "For example, 40 cleaning requests out of 100 total is 40%; the same 40 cleaning requests out of 80 total is 50%. The share increased without any extra cleaning requests. A larger share therefore does not establish dirtier streets, and this chart excludes records with no district. It contains no adjustment for residents, visitors, or willingness and ability to report.",
        },
        {
            "title": "How requests reach the council: mobile, web and telephone",
            "figures": ["channels"], "table": "area_channel_shares",
            "alt": "Reporting-channel shares within request areas, with mobile prominent for cleaning and web for the administrative portal.",
            "how_to_read": "Each horizontal bar represents all reports in one request area. Read the English labels first; the original published labels appear underneath in parentheses. Its coloured segments show reporting-channel shares; Other / missing preserves the channels outside the five displayed leaders. These are display translations, not merged categories.",
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
            "title": "How many days pass before a request is marked closed",
            "figures": ["lag"], "table": "closure_lag",
            "alt": "Counts in recorded closure-lag groups, retaining lags above 60 days in a separate final group.",
            "how_to_read": "Count calendar days from the date a request entered IRIS to the date it was marked closed. For example, 1 March to 4 March is 3 days; 0 means both dates are the same. Each bar counts requests in the stated range. The final More than 60 bar includes every request taking longer than 60 days, so the ranges are not equally wide.",
            "finding": (
                f"Half the requests were marked closed within {lag.median():g} days. "
                f"About 95 out of every 100 were marked closed within {lag.quantile(.95):g} days. "
                f"But {over_sixty:,} requests ({over_sixty / len(cohort) * 100:.1f}%) "
                f"took more than 60 days, and the longest interval in this group was {lag.max():g} days."
            ),
            "meaning": "A single typical time can hide very different experiences. Some requests stay in the administrative process for weeks or months. Statisticians call this smaller group of much longer times a long tail. Here it is visible in the bars on the right, including More than 60; it is not left out of the chart. Showing it helps us remember the people whose requests took much longer to be marked closed.",
            "limit": "Marked closed does not necessarily mean the street was repaired, the question was answered satisfactorily, or the person considered the issue resolved. Still-open requests and requests closed after 2025 are absent, so this chart cannot describe how long every resident waited. The full export's longer maximum of " + f"{frame['closure_lag_days'].max():g} days includes earlier registrations and belongs to a different comparison.",
        },
        {
            "title": "Time until a request is marked closed varies by category",
            "figures": ["area_lag"], "table": "areas",
            "alt": "Median recorded closure lag by leading request area, with dot size and labels showing report counts.",
            "how_to_read": "Each row is a request category, labelled in English and the original language. A dot farther right means more days between registration and being marked closed for the middle request in that category (the median). Larger dots and their numbers mean more requests, not longer times. The chart covers the 12 most frequent categories.",
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
            "title": "Daily request counts and time until closure",
            "figures": ["scatter"], "table": "daily",
            "alt": "Daily observed report counts against median closure lag, coloured by the share missing district.",
            "how_to_read": "Each dot represents the requests registered on one day. Further right means more requests arrived that day. Higher means more days passed before the middle request in that group was marked closed (the median). Colour shows the percentage without a recorded district.",
            "finding": (
                f"Across {daily['median_closure_lag_days'].notna().sum()} observed days, "
                f"the correlation is {corr_text}. This measure describes how consistently "
                "the two quantities move together in a straight-line pattern. A value "
                "close to zero, as here, indicates little such alignment; the dots do "
                "not form a clear rising line."
            ),
            "meaning": "It is understandable to wonder whether more incoming requests mean longer waits. Here, the number of requests registered in a day gives little indication of the time until the middle request in that group was marked closed. That directs attention to more specific questions about the kinds of requests received and the processes they enter.",
            "limit": "The vertical axis is not how long that day's workload took to clear, and the plot does not measure backlog or staffing. Daily medians can hide long individual lags. Calendar effects, request mix, and the closure-year cutoff remain unadjusted, so a weak correlation cannot prove that workload has no effect.",
        },
        {
            "title": "Changing category names can mislead comparisons over time",
            "figures": ["types"], "table": "request_type_monthly",
            "alt": "Monthly shares of unmerged source request-type labels, showing a transition from Catalan to English labels late in 2025.",
            "how_to_read": "Rows keep each published request-type label separate, with an English reading label where needed; columns are registration months. Each cell is that label's share of the month's records. A <1% label indicates a small nonzero share.",
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
        "district_mix": "This compares the topics of requests within each district. It does not rank districts or neighbourhoods from best to worst.",
        "channels": "Street-related reports and administrative questions often reach the council through different channels.",
        "lag": f"Half the requests were marked closed within {lag.median():g} days, but {over_sixty:,} took more than 60 days. Marked closed does not necessarily mean the issue was fixed.",
        "area_lag": "A single citywide closure-time figure cannot describe every kind of request fairly.",
        "scatter": "Knowing how many reports arrived on a day tells us little about their typical recorded closure time in this comparison.",
        "types": "A change in published labels can look like a change in city problems unless we check the definitions.",
    }
    for story in stories:
        story["takeaway"] = takeaways[story["figures"][0]]
    return stories
