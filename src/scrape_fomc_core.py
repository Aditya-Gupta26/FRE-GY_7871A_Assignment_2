"""
Scrape FOMC statements, minutes, and press-conference transcripts from
federalreserve.gov for every meeting date in config.FOMC_MEETING_DATES
(plus the 2020 special/unscheduled statements).

Design notes:
- Every fetched page/PDF is cached under data/raw/ so re-running this script
  doesn't hammer the Fed's servers.
- Text is extracted from the `<div id="article">` container, which is present
  on both statement and minutes pages across the full 2018-2026 window
  (verified directly against pages from 2018, 2020, and 2026).
- Release time conventions (documented, not scraped, where the page itself
  doesn't state a time):
    - Statements: scraped from the page's own "releaseTime" paragraph
      (e.g. "For release at 2:00 p.m. EST").
    - Minutes: released at 2:00 p.m. ET by longstanding, publicly documented
      Fed convention; the page itself does not restate this, so we assume it.
    - Press conferences: begin at 2:30 p.m. ET immediately following the
      2:00 p.m. statement, again by publicly documented convention rather
      than an explicit statement on the page.
  These assumptions are recorded here explicitly so they can be revisited.

BUG FIX: minutes are NOT published on the meeting date - they come out
~3 weeks later. The original version of this script
stored the meeting date as the minutes' "date" field, which downstream
(event_study.py) was read as the release date - silently computing the
wrong market-reaction window for every minutes document.

`scrape_minutes()` now computes the true publication date as the Fed's own
consistently stated, publicly documented policy: "three weeks [21 calendar
days] after the day of the policy decision." This was verified against 5
independently-confirmed real release dates spanning 2018-2026 (including a
December/holiday-season meeting) - all 5 matched exactly.

An earlier version of this fix tried scraping the page's own
`id="lastUpdate"` div instead, on the assumption it would hold the true
publication date. That assumption was WRONG and caught before shipping:
for the Sept 21-22, 2021 meeting, `lastUpdate` read "November 26, 2021" -
but the minutes were actually released October 13, 2021 (confirmed via
independent search), a 44-day discrepancy. `lastUpdate` reflects whenever
the page was last technically touched (e.g. an unrelated later edit), not
necessarily the original release - so it is now used only as a diagnostic
cross-check against the computed date, never as the source of truth.
`date` (the meeting date, used for the URL and as the cross-table join
key) is untouched.
"""
import time
import json
import re
from datetime import datetime, timedelta
from pathlib import Path

import requests
from bs4 import BeautifulSoup
import pdfplumber

from config import (
    FED_BASE, HEADERS, REQUEST_DELAY_SECONDS, DATA_RAW, DATA_PROCESSED,
    FOMC_MEETING_DATES, FOMC_SPECIAL_STATEMENT_DATES, WARSH_SWORN_IN_DATE,
)

STATEMENT_DIR = DATA_RAW / "statements"
MINUTES_DIR = DATA_RAW / "minutes"
PRESCONF_DIR = DATA_RAW / "presconf"
for d in (STATEMENT_DIR, MINUTES_DIR, PRESCONF_DIR):
    d.mkdir(parents=True, exist_ok=True)


def _get(url: str) -> requests.Response | None:
    try:
        resp = requests.get(url, headers=HEADERS, timeout=20)
        time.sleep(REQUEST_DELAY_SECONDS)
        if resp.status_code == 200:
            return resp
        return None
    except requests.RequestException as e:
        print(f"  ! request failed for {url}: {e}")
        return None


def _cached_fetch_html(url: str, cache_path: Path) -> str | None:
    if cache_path.exists():
        return cache_path.read_text(encoding="utf-8")
    resp = _get(url)
    if resp is None:
        return None
    cache_path.write_text(resp.text, encoding="utf-8")
    return resp.text


def _cached_fetch_binary(url: str, cache_path: Path) -> bytes | None:
    if cache_path.exists():
        return cache_path.read_bytes()
    resp = _get(url)
    if resp is None:
        return None
    cache_path.write_bytes(resp.content)
    return resp.content


def extract_article_text(html: str) -> str:
    """Extract body paragraphs from the div#article container, dropping
    known UI paragraph classes (release time, article date, share widgets)."""
    soup = BeautifulSoup(html, "lxml")
    container = soup.find(id="article") or soup.find(id="content")
    if container is None:
        return ""
    parts = []
    for p in container.find_all("p"):
        classes = p.get("class") or []
        if any(c in ("releaseTime", "article__time") for c in classes):
            continue
        text = p.get_text(" ", strip=True)
        if text:
            parts.append(text)
    return "\n\n".join(parts)


def extract_release_time(html: str) -> str | None:
    soup = BeautifulSoup(html, "lxml")
    tag = soup.find("p", class_="releaseTime")
    if tag:
        return tag.get_text(" ", strip=True).replace("For release at", "").strip()
    return None


def compute_minutes_release_date(meeting_end_date: str) -> str:
    """Minutes release date per the Fed's own stated policy: 21 calendar
    days after the meeting's second day. Verified against 5 independently
    confirmed real dates 2018-2026 (see module docstring) - all matched
    exactly, including across a December/holiday-season meeting."""
    d = datetime.strptime(meeting_end_date, "%Y%m%d")
    return (d + timedelta(days=21)).strftime("%Y%m%d")


def extract_last_update_date(html: str) -> str | None:
    """Parse the page's `id="lastUpdate"` div (e.g. "Last Update: August 19,
    2026") into YYYYMMDD. NOT trustworthy as the true release date on its
    own (see BUG FIX note in the module docstring - it can reflect a later,
    unrelated page edit) - used only as a diagnostic cross-check against
    compute_minutes_release_date()."""
    soup = BeautifulSoup(html, "lxml")
    tag = soup.find(id="lastUpdate")
    if tag is None:
        return None
    raw = tag.get_text(" ", strip=True).replace("Last Update:", "").strip()
    raw = re.sub(r"\s+", " ", raw)
    try:
        return datetime.strptime(raw, "%B %d, %Y").strftime("%Y%m%d")
    except ValueError:
        return None


def scrape_statement(date: str) -> dict | None:
    url = f"{FED_BASE}/newsevents/pressreleases/monetary{date}a.htm"
    cache = STATEMENT_DIR / f"{date}.htm"
    html = _cached_fetch_html(url, cache)
    if html is None:
        return None
    text = extract_article_text(html)
    if len(text.split()) < 20:
        print(f"  ! statement {date}: suspiciously short extraction ({len(text.split())} words)")
    return {
        "date": date,
        "doc_type": "statement",
        "url": url,
        "release_time_raw": extract_release_time(html),
        "text": text,
        "n_words": len(text.split()),
    }


def scrape_minutes(date: str) -> dict | None:
    url = f"{FED_BASE}/monetarypolicy/fomcminutes{date}.htm"
    cache = MINUTES_DIR / f"{date}.htm"
    html = _cached_fetch_html(url, cache)
    if html is None:
        return None
    text = extract_article_text(html)
    if len(text.split()) < 50:
        print(f"  ! minutes {date}: suspiciously short extraction ({len(text.split())} words)")

    actual_release_date = compute_minutes_release_date(date)
    last_update = extract_last_update_date(html)
    if last_update is not None:
        gap = abs((datetime.strptime(last_update, "%Y%m%d") - datetime.strptime(actual_release_date, "%Y%m%d")).days)
        if gap > 3:
            print(f"  ! minutes {date}: computed release {actual_release_date} vs. page's lastUpdate "
                  f"{last_update} differ by {gap} days - using the computed date (see module docstring "
                  f"on why lastUpdate isn't trusted alone); worth a manual look if this list is long")

    return {
        "date": date,  # meeting date - unchanged, still the cross-table join key
        "doc_type": "minutes",
        "url": url,
        "release_time_raw": "2:00 p.m. ET (documented Fed convention; not restated on page)",
        "actual_release_date": actual_release_date,  # true publication date, ~3 weeks later
        "text": text,
        "n_words": len(text.split()),
    }


def scrape_presconf(date: str) -> dict | None:
    url = f"{FED_BASE}/mediacenter/files/FOMCpresconf{date}.pdf"
    cache = PRESCONF_DIR / f"{date}.pdf"
    content = _cached_fetch_binary(url, cache)
    if content is None:
        return None
    try:
        with pdfplumber.open(cache) as pdf:
            text = "\n\n".join(page.extract_text() or "" for page in pdf.pages)
    except Exception as e:
        print(f"  ! presconf {date}: PDF parse failed: {e}")
        return None
    if len(text.split()) < 200:
        print(f"  ! presconf {date}: suspiciously short extraction ({len(text.split())} words)")
    return {
        "date": date,
        "doc_type": "presconf",
        "url": url,
        "release_time_raw": "2:30 p.m. ET (documented Fed convention, follows the 2:00 p.m. statement; not restated on page)",
        "text": text,
        "n_words": len(text.split()),
    }


def attribute_chair(date: str) -> str:
    return "Warsh" if date >= WARSH_SWORN_IN_DATE else "Powell"


def main():
    records = []
    all_dates = sorted(set(FOMC_MEETING_DATES) | set(FOMC_SPECIAL_STATEMENT_DATES))

    print(f"Scraping {len(all_dates)} meeting/statement dates...")
    for date in all_dates:
        print(f"-- {date} --")
        stmt = scrape_statement(date)
        if stmt:
            stmt["chair"] = attribute_chair(date)
            stmt["is_special_statement"] = date in FOMC_SPECIAL_STATEMENT_DATES
            records.append(stmt)
        else:
            print(f"  no statement found for {date}")

        if date in FOMC_MEETING_DATES:  # minutes/presconf only for regular meetings
            minutes = scrape_minutes(date)
            if minutes:
                minutes["chair"] = attribute_chair(date)
                minutes["is_special_statement"] = False
                records.append(minutes)

            presconf = scrape_presconf(date)
            if presconf:
                presconf["chair"] = attribute_chair(date)
                presconf["is_special_statement"] = False
                records.append(presconf)

    out_path = DATA_PROCESSED / "fomc_core_documents.json"
    out_path.write_text(json.dumps(records, indent=2), encoding="utf-8")
    print(f"\nSaved {len(records)} documents to {out_path}")

    by_type = {}
    for r in records:
        by_type[r["doc_type"]] = by_type.get(r["doc_type"], 0) + 1
    print("Counts by type:", by_type)


if __name__ == "__main__":
    main()
