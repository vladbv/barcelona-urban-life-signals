"""Write an evidence-led Markdown guide and a self-contained, shareable HTML report."""

from __future__ import annotations

import base64
import hashlib
import html
import json
import os
import platform
import re
from pathlib import Path

import matplotlib
import pandas as pd

from src.iris_signals import COHORT_NOTE, registration_cohort
from src.iris_interpretations import READING_APPROACH, READING_GLOSSARY, plot_readings
from src.profile_iris import markdown_table

SOURCE_URL = "https://opendata-ajuntament.barcelona.cat/data/en/dataset/iris"
RESOURCE_ID = "efc9fd4d-a812-427c-846d-a086d22012a4"
README_START = "<!-- BEGIN IRIS PLOT READINGS -->"
README_END = "<!-- END IRIS PLOT READINGS -->"


def plot_markdown(section: dict, number: int, figures: dict, parent: Path, heading: str) -> str:
    paragraphs = [f"{heading} {number}. {section['title']}"]
    for name in section["figures"]:
        relative = os.path.relpath(figures[name], parent)
        paragraphs.append(f"![{section['alt']}]({relative})")
    paragraphs.extend([
        f"**Takeaway: {section['takeaway']}**",
        f"*How to read it: {section['how_to_read']}*", section["finding"],
        section["meaning"], section["limit"],
    ])
    return "\n\n".join(paragraphs)


def update_readme(path: Path, sections: list[dict], figures: dict) -> None:
    """Replace only the explicitly marked plot tour; preserve the authored README."""
    original = path.read_text(encoding="utf-8")
    if original.count(README_START) != 1 or original.count(README_END) != 1:
        raise ValueError(f"{path} must contain one {README_START} and one {README_END} marker.")
    start = original.index(README_START) + len(README_START)
    end = original.index(README_END)
    if end < start:
        raise ValueError(f"Plot-reading markers are out of order in {path}.")
    navigation = []
    for i, section in enumerate(sections, 1):
        slug = re.sub(r"[^\w -]", "", section["title"].lower()).replace(" ", "-")
        navigation.append(f"[{i}. {section['title']}](#{i}-{slug})")
    body = "\n\n".join([
        "## A walk through the plots", READING_APPROACH,
        "#### A few words, explained simply",
        markdown_table(pd.DataFrame(READING_GLOSSARY, columns=["Word", "Plain meaning"])),
        "All thirteen plots are shown below. Follow the story in order, or jump to a reading:",
        "\n".join(f"- {link}" for link in navigation),
        *(plot_markdown(section, i, figures, path.parent, "###") for i, section in enumerate(sections, 1)),
    ])
    path.write_text(original[:start] + "\n\n" + body + "\n\n" + original[end:], encoding="utf-8")


def sha256(path: Path) -> str:
    with path.open("rb") as stream:
        return hashlib.file_digest(stream, "sha256").hexdigest()


def make_manifest(frame: pd.DataFrame, tables: dict, args) -> dict:
    manifest = {
        "source_dataset_url": SOURCE_URL,
        "resource_id": RESOURCE_ID,
        "processed_input": {"path": str(args.input_path), "sha256": sha256(args.input_path)},
        "processed_records": len(frame),
        "headline_records": len(registration_cohort(frame)),
        "headline_registration_start": "2025-01-01",
        "headline_registration_end": "2025-12-31",
        "selection": COHORT_NOTE,
        "validation": "Unique nonmissing IDs, valid dates, 2025 closures, nonnegative lags matching dates.",
        "calendar": "365 calendar days; zero observed records filled as zero; lag stays undefined on empty days; trailing window requires 7 days.",
        "percentages": "Full displayed-group denominators, with Other / missing for omitted categories.",
        "category_policy": "Preserve published request_type labels; no unverified language crosswalk.",
        "versions": {"python": platform.python_version(), "pandas": pd.__version__, "matplotlib": matplotlib.__version__},
        "tables": {name: {"path": str(args.tables_dir / f"iris_{name}.csv"), "rows": len(table)} for name, table in tables.items()},
    }
    raw_path = Path("data/raw/2025_IRIS_Peticions_Ciutadanes_OpenData.csv")
    if raw_path.is_file() and args.input_path == Path("data/processed/iris_2025_clean.csv"):
        manifest["local_raw_reference"] = {"path": str(raw_path), "sha256": sha256(raw_path)}
    return manifest


def write_reports(frame: pd.DataFrame, tables: dict, figures: dict, args) -> None:
    sections = plot_readings(frame, tables)
    manifest = make_manifest(frame, tables, args)
    cohort = registration_cohort(frame)
    talk = (
        f"We are looking at {len(cohort):,} citizen reports registered and closed in 2025. "
        "Reporting follows a strong weekly rhythm, and cleaning and public-space maintenance "
        f"make up {tables['areas'].head(2)['share_percent'].sum():.1f}% of this cohort. "
        f"But {cohort['district'].isna().mean() * 100:.1f}% have no district, with coverage "
        "varying strongly by category and channel. Requests closed after year-end are absent, "
        "so late-year declines cannot be read as falling demand. Published request-type labels "
        "also change during the year. This is a useful description of reported activity; "
        "weather effects, causes, and service performance need further evidence."
    )
    methods = [
        "Remove exact duplicate raw rows only; preserve observed category labels and missing geography. Raw downloads remain unchanged.",
        "Headline cohort: registration_date in 2025 within the inspected export whose closure_date is in 2025. Older registrations are retained in the processed file.",
        "Daily counts use all 365 calendar days. Weekday means divide by calendar exposure (including zero-record days); the trailing average requires seven complete days.",
        "District and channel compositions retain every record in their displayed group, using Other / missing for omitted categories. District composition excludes missing districts explicitly.",
        "Lags are calendar-day differences between published dates, not working days or verified resolution times. The histogram has unequal-width groups and an explicit >60-day group.",
        "Scatter plots include every day with defined lag; Pearson correlation is descriptive only. No minimum-volume threshold or statistical significance claim is used.",
        "Source labels remain in Catalan/English for traceability. Descriptions translate the broad meaning; they do not replace the source categories.",
        "The monthly table also includes closures_all_export, which counts all deduplicated closures including earlier registrations. It uses a different cohort from the headline registration counts.",
    ]
    markdown = [
        "# Reading Barcelona's reported civic activity", "## Scope and headline cohort", COHORT_NOTE,
        f"Source: [Open Data BCN — IRIS]({SOURCE_URL}), resource `{RESOURCE_ID}`. "
        f"Processed input: `{args.input_path}` ({len(frame):,} records).",
        "## A one-minute explanation", talk,
        "## How to read the plots", READING_APPROACH,
        markdown_table(pd.DataFrame(READING_GLOSSARY, columns=["Word", "Plain meaning"])),
    ]
    for i, section in enumerate(sections, 1):
        markdown.append(plot_markdown(section, i, figures, args.report_path.parent, "##"))
        markdown.extend([
            f"<details>\n<summary>Inspect supporting data: iris_{section['table']}.csv (first 12 rows)</summary>",
            markdown_table(tables[section["table"]].head(12).round(2)), "</details>",
        ])
    markdown.extend(["## Reproducible methods", "\n".join(f"- {method}" for method in methods),
                     "## What comes next", "Before weather integration, inspect adjacent closure-year resources and document a common observation window. Validate request-type label mappings against publisher metadata. Then define a specific weather question and an appropriate station/time resolution. No weather effect, recurring seasonality, causal claim, or forecast is established by this report.",
                     "## Data and provenance", f"Aggregate tables: `{args.tables_dir}`. Standalone HTML: `{args.html_path}`. Input fingerprints and generation rules: `{args.manifest_path}`.",
                     f"Processed SHA-256: `{manifest['processed_input']['sha256']}`."])

    e = html.escape
    cards = "".join(f'<div class="metric"><strong>{value}</strong><span>{label}</span></div>' for value, label in [
        (f"{len(cohort):,}", "registered & closed in 2025"),
        (f"{cohort['district'].isna().mean() * 100:.1f}%", "missing district"),
        (f"{cohort['closure_lag_days'].median():.0f} days", "median recorded closure lag"),
    ])
    contents = []
    for i, section in enumerate(sections, 1):
        pictures = []
        for name in section["figures"]:
            encoded = base64.b64encode(figures[name].read_bytes()).decode("ascii")
            pictures.append(f'<figure><img src="data:image/png;base64,{encoded}" alt="{e(section["alt"])}" loading="lazy"><figcaption>{e(section["how_to_read"])}</figcaption></figure>')
        table = tables[section["table"]]
        preview = table.head(12).round(2).to_html(index=False, border=0, na_rep="—")
        contents.append(f'<section id="reading-{i}"><p class="eyebrow">Reading {i:02}</p><h2>{e(section["title"])}</h2>'
                        f'{"".join(pictures)}<p><strong>Takeaway: {e(section["takeaway"])}</strong></p>'
                        f'<p class="finding">{e(section["finding"])}</p><p>{e(section["meaning"])}</p>'
                        f'<p class="boundary">{e(section["limit"])}</p>'
                        f'<details><summary>Inspect supporting data · {len(table)} rows (first 12 shown)</summary><div class="table-wrap">{preview}</div></details></section>')
    downloads = []
    for name, table in tables.items():
        encoded = base64.b64encode(table.to_csv(index=False, float_format="%.6f").encode("utf-8")).decode("ascii")
        downloads.append(f'<a class="download" download="iris_{name}.csv" href="data:text/csv;base64,{encoded}">{e(name.replace("_", " "))} ↓</a>')
    navigation = "".join(f'<a href="#reading-{i}">{i:02} {e(section["title"])}</a>' for i, section in enumerate(sections, 1))
    html_document = f'''<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Barcelona Urban Life Signals · Reading the 2025 IRIS cohort</title>
<style>
:root {{color-scheme:light;--sea:#174c5e;--ink:#2f241d;--paper:#fff8ef;--tile:#e6a23c;--muted:#69594c}}
*{{box-sizing:border-box}}html{{scroll-behavior:smooth}}body{{margin:0;background:var(--paper);color:var(--ink);font:17px/1.65 system-ui,sans-serif}}
header{{background:var(--sea);color:var(--paper);padding:64px max(6vw,24px) 48px}}header p{{max-width:850px}}h1{{font-size:clamp(2.4rem,5vw,4.8rem);line-height:1.07;max-width:1000px;margin:16px 0 28px;letter-spacing:-.04em}}h2{{color:var(--sea);font-size:clamp(1.6rem,3vw,2.2rem);line-height:1.2}}
.eyebrow{{text-transform:uppercase;letter-spacing:.14em;font-size:.76rem;font-weight:750}}header .eyebrow{{color:#f8cc82}}main{{max-width:1160px;margin:auto;padding:32px 24px 64px}}section{{padding:35px 0;border-bottom:1px solid #dbcbb9;scroll-margin-top:20px}}
.metrics{{display:grid;grid-template-columns:repeat(3,1fr);gap:18px;max-width:1000px;margin-top:34px}}.metric{{border-top:2px solid #e6a23c;padding:15px 0}}.metric strong{{display:block;font-size:2rem}}.metric span{{font-size:.92rem}}.finding{{font-size:1.17rem;max-width:1000px}}aside{{background:#f2e4cf;border-left:4px solid var(--tile);padding:18px 22px;margin:24px 0}}
figure{{margin:22px 0}}img{{display:block;width:100%;height:auto}}a{{color:var(--sea);text-underline-offset:3px}}nav{{display:grid;grid-template-columns:1fr 1fr;gap:10px;padding:18px 0}}nav a{{font-size:.95rem}}summary{{cursor:pointer;font-weight:650;padding:14px 0}}.table-wrap{{overflow-x:auto}}table{{border-collapse:collapse;font-size:.82rem;width:100%}}td,th{{text-align:left;padding:10px;border-bottom:1px solid #ddd}}th{{background:#eee4d6}}.downloads{{display:flex;flex-wrap:wrap;gap:10px}}.download{{padding:8px 12px;border:1px solid #bba98f;border-radius:5px;text-decoration:none;font-size:.9rem}}.muted{{color:var(--muted);font-size:.9rem}}code{{overflow-wrap:anywhere}}blockquote{{margin:0;font-size:1.16rem;border-left:4px solid var(--sea);padding:12px 24px}}li{{margin-bottom:10px}}footer{{margin-top:28px;font-size:.85rem;color:var(--muted)}}
figcaption{{color:var(--muted);font-size:.92rem;padding:12px 0}}.boundary{{border-left:3px solid #c4a071;padding-left:20px;color:var(--muted)}}
@media(max-width:650px){{header{{padding:36px 24px}}.metrics,nav{{grid-template-columns:1fr}}main{{padding:20px 16px}}.metric{{padding:8px 0}}.metric strong{{font-size:1.6rem}}}}
@media print{{header{{background:white;color:#174c5e;padding:16px 0}}header .eyebrow{{color:#174c5e}}nav,.downloads{{display:none}}main{{padding:0}}section{{break-before:auto}}figure,aside{{break-inside:avoid}}details{{display:none}}body{{font-size:11pt}}}}
</style></head><body>
<header><p class="eyebrow">Barcelona Urban Life Signals / IRIS / 2025 cohort</p>
<h1>What citizen reports<br>make visible.</h1><p>A reading guide to reporting rhythms, public-space requests, and the limits of the evidence.</p><div class="metrics">{cards}</div></header>
<main><aside><strong>Start with the cohort.</strong> {e(COHORT_NOTE)}</aside><nav aria-label="Report contents">{navigation}</nav>
<section><p class="eyebrow">For a conversation or presentation</p><h2>The one-minute explanation</h2><blockquote>{e(talk)}</blockquote></section>
<p class="muted">{e(READING_APPROACH)}</p>
<details><summary>A few words, explained simply</summary><dl>{"".join(f"<dt><strong>{e(term)}</strong></dt><dd>{e(meaning)}</dd>" for term, meaning in READING_GLOSSARY)}</dl></details>
{"".join(contents)}
<section><p class="eyebrow">Evidence you can inspect</p><h2>Aggregate data, ready to use</h2><p>Download the complete tables behind these readings. All charts and CSVs are embedded in this file; it works offline and can be shared on its own.</p><div class="downloads">{"".join(downloads)}</div></section>
<section><h2>How this report was made</h2><ul>{''.join(f'<li>{e(method)}</li>' for method in methods)}</ul>
<p>Source: <a href="{SOURCE_URL}">Open Data BCN · IRIS</a>. Resource ID: <code>{RESOURCE_ID}</code>.</p>
<p>{len(frame):,} deduplicated records; {len(frame) - len(cohort):,} earlier registrations retained outside the headline cohort. No weather data or causal model has been fitted.</p>
<p>Processed input SHA-256: <code>{manifest['processed_input']['sha256']}</code>.</p>
<p>Next: inspect adjacent closure-year resources, define comparable follow-up windows, and validate source label mappings before adding weather context.</p></section>
<footer>Generated from the local inspected snapshot with Python {platform.python_version()}, pandas {pd.__version__}, matplotlib {matplotlib.__version__}. Reported citizen activity is not complete ground truth about Barcelona.</footer>
</main></body></html>'''
    for path, content in [
        (args.report_path, "\n\n".join(markdown) + "\n"),
        (args.html_path, html_document),
        (args.manifest_path, json.dumps(manifest, indent=2, ensure_ascii=False) + "\n"),
    ]:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8")
    if args.readme_path is not None:
        update_readme(args.readme_path, sections, figures)
