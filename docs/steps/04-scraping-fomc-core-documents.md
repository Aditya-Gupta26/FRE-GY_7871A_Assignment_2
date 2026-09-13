# Step 4: Scraping FOMC Core Documents

This is where the project's actual data collection began: statements, minutes, and press-conference transcripts for every FOMC meeting from 2018 through 2026.

## The problem: we needed exact URLs and exact meeting dates, not guesses

The assignment requires *every* FOMC statement, minutes set, and press-conference transcript from February 2018 (Powell's start) through today. Guessing at URL patterns or approximate meeting dates would silently drop documents or scrape the wrong pages. So before writing the scraper, we did real reconnaissance against the live site using `curl` and `WebFetch`:

- Fetched `federalreserve.gov/monetarypolicy/fomccalendars.htm` (covers recent years) and found it links to pages like `/newsevents/pressreleases/monetary20260617a.htm` (statements) and `/monetarypolicy/fomcminutes20260617.htm` (minutes) — but it only goes back to 2021.
- For 2018–2020, the Fed keeps separate historical pages (`fomchistorical2018.htm`, etc.) — confirmed these exist and contain the same URL pattern.
- Confirmed press-conference transcripts live at a *different* path entirely: `/mediacenter/files/FOMCpresconf{date}.pdf` (a PDF, not HTML).
- Pulled the **complete, real list of every FOMC meeting minutes link from 2021–2026** directly out of the calendar page's HTML via `grep`, rather than typing dates from memory — this is the kind of detail that's easy to get subtly wrong (an extra or missing meeting) if hand-transcribed.
- Fetched an actual 2018 statement and an actual 2026 statement (Warsh's first, June 17, 2026) to confirm the page structure — specifically the release-time text ("For release at 2:00 p.m. EST") and the exact HTML container holding the body text — was stable across 8 years, not just assumed to be.

**Why this mattered:** the assignment specifically requires us to record each document's **release date and time** — not just date — because that detail later determines which market-close window is the correct one to measure (see [Step 10](10-event-study.md)). Confirming the release-time text lived in a consistent `<p class="releaseTime">` tag, present on the earliest and latest pages we checked, meant we could extract it reliably in code rather than hand-coding it per era.

## `src/config.py`

**What it does:** holds every constant shared across the whole project — file paths (`DATA_RAW`, `DATA_PROCESSED`), HTTP headers (a descriptive User-Agent identifying this as NYU coursework, not an anonymous bot), a politeness delay between requests, and — most importantly — the **complete, verified list of every FOMC meeting date from January 2018 through July 2026** (69 regular meetings), plus four 2020 "special" statement dates (the unscheduled emergency COVID-era actions: March 3, March 23, March 31, and the August 27 framework announcement, which don't follow the normal 8-per-year meeting cadence). It also defines the exact chair-tenure boundary dates (`POWELL_SWORN_IN_DATE`, `POWELL_LAST_DAY_AS_CHAIR`, `WARSH_SWORN_IN_DATE`) used everywhere downstream to attribute a document to the correct chair.

**Why it was necessary:** every other script in the project imports from this file. Centralizing the meeting-date list and chair-boundary dates in one place means there is exactly one place to get them right (or wrong) — not 18 separate hardcoded copies scattered across scripts that could silently drift out of sync.

**Result:** a single source of truth reused by every scraper, the corpus builder, the tone scorers, and the forecast model.

## `src/scrape_utils.py`

**What it does:** three small, shared functions used by *every* scraper in the project (this one and the speeches/testimony one in [Step 5](05-scraping-speeches-and-testimony.md)):
- `get()` / `cached_fetch_html()` / `cached_fetch_binary()` — fetch a URL with a polite delay, but check a local cache file first so re-running the pipeline never re-hits the Fed's servers for a document already downloaded.
- `extract_article_text()` — pulls the actual body paragraphs out of a Fed webpage, specifically from the `<div id="article">` container (confirmed present on statement, minutes, speech, and testimony pages alike), while dropping known non-content paragraphs (the release-time line, the article-date line).
- `extract_release_time()` / `extract_article_date()` — pull the human-readable release time/date text directly off the page.

**Why it was necessary:** without caching, every re-run of the pipeline (and there were several, as bugs got fixed downstream) would re-scrape all 311 documents from scratch — slow, and impolite to a public government website. Without the shared text-extraction function, we'd have needed to hand-tune HTML-parsing logic separately for statements, minutes, speeches, and testimony, even though they turned out to share the same underlying page template.

**Result:** every downstream scraper is ~40 lines of "what URL pattern, what date range" logic on top of this shared foundation, not a reimplementation of HTTP fetching and HTML parsing each time.

## `src/scrape_fomc_core.py`

**What it does:** the actual scraper for statements, minutes, and press-conference transcripts. For every date in `config.FOMC_MEETING_DATES` (plus the four special 2020 dates), it:
1. Fetches the statement page, extracts its text and its stated release time.
2. For regular meetings only, fetches the minutes page (no explicit release time on the page itself — we document the well-known convention of 2:00 p.m. ET as an explicit, stated assumption, not a silent guess) and the press-conference PDF (parsed via `pdfplumber`, with a similarly documented 2:30 p.m. ET convention).
3. Tags every document with the correct chair, using the boundary dates from `config.py` — including correctly handling the narrow May 15–22, 2026 window where Powell was "chair pro tempore" but not the confirmed Chair, which we attribute to Powell rather than treating as a gap or misattributing to Warsh.
4. Flags anything under 20 (statements) or 50 (minutes) words as suspiciously short, so a silent extraction failure would show up in the console output rather than pass unnoticed into the dataset.

**Why it was necessary:** this is the direct implementation of the assignment's first data requirement — the corpus of statements, minutes, and press-conference transcripts — using the exact URL patterns and page structure confirmed by the reconnaissance above.

**Result, from the actual run:**
- **73 statements**, **69 minutes**, **65 press-conference transcripts** — 207 documents total.
- **Zero suspiciously-short extractions** across the entire run.
- Correctly captured both of Warsh's meetings as Chair (June 17 and July 29, 2026) with substantial text (e.g., the July 29 press-conference transcript alone ran to 7,009 words).
- The count of 65 (not 69) press conferences is itself a correct, expected result, not a bug: the Fed only started holding a press conference after *every* meeting starting in 2019; before that (2018), only 4 of that year's 8 meetings had one — the scraper simply found what's actually there rather than forcing a number.

This was the first commit pushed to the GitHub repo, bundled with the market-data script from [Step 6](06-collecting-market-data.md) and the scaffold from [Step 3](03-environment-and-repo-setup.md).

**Next:** [Step 5 — Scraping Speeches & Testimony](05-scraping-speeches-and-testimony.md).
