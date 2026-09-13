"""
Scrape Chair speeches and testimony from federalreserve.gov, 2018-2026.

Approach: the yearly archive pages (/newsevents/{year}-speeches.htm and
-testimony.htm) link to individual pages named {speaker}{YYYYMMDD}a.htm,
which lets us filter directly by speaker surname in the URL rather than
guessing dates. We then keep only documents that fall within that
speaker's actual tenure AS CHAIR (see config.py boundaries) - a Powell
speech given after he stopped being Chair (2026-05-15) is excluded, even
though he remains a Fed Governor and keeps giving speeches.
"""
import re
import json

from bs4 import BeautifulSoup

from config import (
    FED_BASE, DATA_RAW, DATA_PROCESSED,
    POWELL_SWORN_IN_DATE, POWELL_LAST_DAY_AS_CHAIR, WARSH_SWORN_IN_DATE,
)
from scrape_utils import cached_fetch_html, extract_article_text, extract_article_date

YEARS = range(2018, 2027)
LINK_RE = re.compile(r'href="(/newsevents/(speech|testimony)/(powell|warsh)(\d{8})a\.htm)"')

SPEECH_DIR = DATA_RAW / "speeches"
TESTIMONY_DIR = DATA_RAW / "testimony"
for d in (SPEECH_DIR, TESTIMONY_DIR):
    d.mkdir(parents=True, exist_ok=True)


def is_chair_period(speaker: str, date: str) -> bool:
    if speaker == "powell":
        return POWELL_SWORN_IN_DATE <= date <= POWELL_LAST_DAY_AS_CHAIR
    if speaker == "warsh":
        return date >= WARSH_SWORN_IN_DATE
    return False


def find_chair_links_for_year(year: int) -> list[tuple[str, str, str]]:
    """Returns list of (kind, speaker, date) for links found on the year's
    speech/testimony index pages, already filtered to chair-period dates."""
    results = []
    for kind in ("speeches", "testimony"):
        url = f"{FED_BASE}/newsevents/{year}-{kind}.htm"
        cache = DATA_RAW / "index_pages" / f"{year}-{kind}.htm"
        cache.parent.mkdir(parents=True, exist_ok=True)
        html = cached_fetch_html(url, cache)
        if html is None:
            print(f"  ! could not fetch index page {url}")
            continue
        for match in LINK_RE.finditer(html):
            _, doc_kind, speaker, date = match.groups()
            if is_chair_period(speaker, date):
                results.append((doc_kind, speaker, date))
    return sorted(set(results), key=lambda x: x[2])


def scrape_one(kind: str, speaker: str, date: str) -> dict | None:
    subdir = "speech" if kind == "speech" else "testimony"
    url = f"{FED_BASE}/newsevents/{subdir}/{speaker}{date}a.htm"
    cache_dir = SPEECH_DIR if kind == "speech" else TESTIMONY_DIR
    cache = cache_dir / f"{speaker}{date}.htm"
    html = cached_fetch_html(url, cache)
    if html is None:
        print(f"  ! fetch failed: {url}")
        return None
    text = extract_article_text(html)
    if len(text.split()) < 100:
        print(f"  ! {speaker}{date}: suspiciously short extraction ({len(text.split())} words)")
    return {
        "date": date,
        "doc_type": kind,  # "speech" or "testimony"
        "chair": "Powell" if speaker == "powell" else "Warsh",
        "url": url,
        "release_time_raw": extract_article_date(html),
        "text": text,
        "n_words": len(text.split()),
    }


def main():
    all_links = []
    for year in YEARS:
        print(f"-- indexing {year} --")
        links = find_chair_links_for_year(year)
        print(f"   found {len(links)} chair-period speech/testimony links")
        all_links.extend(links)

    print(f"\nTotal chair-period speech/testimony documents to scrape: {len(all_links)}")

    records = []
    for kind, speaker, date in all_links:
        rec = scrape_one(kind, speaker, date)
        if rec:
            records.append(rec)

    out_path = DATA_PROCESSED / "speeches_testimony_documents.json"
    out_path.write_text(json.dumps(records, indent=2), encoding="utf-8")
    print(f"\nSaved {len(records)} documents to {out_path}")

    by_type = {}
    for r in records:
        key = (r["doc_type"], r["chair"])
        by_type[key] = by_type.get(key, 0) + 1
    print("Counts by (type, chair):", by_type)


if __name__ == "__main__":
    main()
