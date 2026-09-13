# Step 5: Scraping Speeches & Testimony

The assignment's document requirement explicitly includes "the Chair's speeches (including testimony and press conference transcripts)." Press conferences were covered in [Step 4](04-scraping-fomc-core-documents.md); this step covers standalone speeches and congressional testimony.

## The reconnaissance: a different, and genuinely useful, URL pattern

We checked `federalreserve.gov/newsevents/2026-speeches.htm` and found the Fed publishes one archive page per year, linking to individual pages named `/newsevents/speech/{speaker-surname}{YYYYMMDD}a.htm` — e.g. `warsh20260828a.htm`. The speaker's surname is right there in the URL. That's a much better filtering mechanism than trying to parse speaker names out of page content: we could pull every link matching `powell` or `warsh` directly with a regular expression against the raw archive page HTML, for every year 2018–2026, and know immediately how many candidate documents existed before scraping a single one (79 speeches + 26 testimony across the whole window, confirmed via a quick `grep` count before writing any Python).

## A subtlety that would have silently corrupted the data: "Chair" isn't the same as "person"

Jerome Powell remains a sitting Fed Governor after his term as Chair ended (May 15, 2026) — and he kept giving speeches. A naive filter of "any speech by Powell" would have pulled in post-Chair-tenure Powell speeches and mislabeled them as Chair communications, diluting the Powell-era tone signal with speeches that don't actually represent the Fed's official leadership stance at the time. The fix was straightforward once spotted: filter not just by speaker name, but by whether that *specific date* falls within that *specific person's* actual tenure as Chair, using the boundary dates from `config.py`. Concretely, `powell20260531a.htm` (May 31, 2026 — 16 days after his term ended) is correctly *excluded*, while `warsh20260828a.htm` is correctly *included*.

## `src/scrape_speeches_testimony.py`

**What it does:**
- `find_chair_links_for_year()` fetches each year's speech and testimony archive page and extracts every link matching `(powell|warsh)` with a regex, for every year 2018–2026.
- `is_chair_period()` applies the tenure-boundary filter described above.
- `scrape_one()` fetches each surviving link, reusing `extract_article_text()` from `scrape_utils.py` (the same content-extraction logic that worked for statements and minutes, since speeches use the same page template).

**Why it was necessary:** this is the direct implementation of the assignment's speeches/testimony requirement, with the chair-attribution correctness described above being the specific reason a naive approach wouldn't have worked.

**Result, from the actual run:**
- **78 speeches** (77 Powell, 1 Warsh) and **26 testimony documents** (all Powell — Warsh hadn't testified before Congress as of this writing) — 104 documents total.
- **Zero suspiciously-short extractions.**
- One index page (`2026-testimony.htm`) returned a 404 during the scrape. We didn't just log and move on — we separately verified with a direct `curl` check using the exact same User-Agent the scraper uses, confirmed it's a genuine 404 (the Fed simply hasn't created that page because no testimony has happened in 2026 yet), and concluded no data was actually lost. This distinction — "confirmed nothing is missing" vs. "a request failed and we hoped it didn't matter" — is the kind of check that's easy to skip under time pressure but avoids silently shipping incomplete data.
- Warsh's one speech in the corpus — the August 28, 2026 Jackson Hole address — turned out later to be the single most important document in the whole project: it's the speech that (per real-world reporting we found in [Step 13](13-the-forecast-model.md)) shifted market pricing for the September meeting.

**Next:** [Step 6 — Collecting Market Data](06-collecting-market-data.md).
