# Step 7: Building the Corpus

With both document scrapes complete (207 core documents + 104 speeches/testimony = 311) and living as two separate JSON files, this step merges them into the one unified dataset every later step reads from.

## `src/build_corpus.py`

**What it does:**
- Loads both scraped JSON files and concatenates them into a single table.
- Parses each document's `date` string into an actual datetime column (`date_dt`).
- Computes an approximate **release hour** for every document — the single most important thing this script does. For statements, it parses the actual "For release at 2:00 p.m. EST" text scraped off the page. For minutes and press conferences, it applies the documented convention from [Step 4](04-scraping-fomc-core-documents.md) (2:00 p.m. and 2:30 p.m. ET respectively). For speeches and testimony, where the page gives a date but no time, it makes an explicit, stated assumption (noon) rather than silently defaulting to something arbitrary.
- From that release hour, computes a boolean `released_before_close` (before 4:00 p.m. ET, the standard equity/FX market close) — this single column is what later lets [Step 10](10-event-study.md) decide, per document, whether "the market's reaction" shows up in *that day's* closing price or the *next* day's.

**Why this was necessary, and why it's not a trivial merge:** the assignment specifically requires recording each document's release date *and time* — not as a nice-to-have, but because it changes which comparison is the statistically correct one. A statement released at 2:00 p.m. (while markets are open) should be compared prior-close-to-same-day-close; a hypothetical document released at 6:00 p.m. (after close) needs same-day-close-to-next-day-close instead. Getting this wrong wouldn't just add noise — it would systematically misattribute market moves that happened *before* a document was even public to that document's tone, or miss the reaction entirely by measuring the wrong day.

## Result

`data/processed/corpus.parquet` — the single, authoritative table (311 rows) that every subsequent script (`tone_word_list.py`, `tone_finbert.py`, `event_study.py`, `rate_decisions.py`, and eventually the notebook itself) reads from. Running the script printed a clean summary:

```
Merged corpus: 311 documents
minutes    Powell 67, Warsh 2
presconf   Powell 63, Warsh 2
speech     Powell 77, Warsh 1
statement  Powell 71, Warsh 2
testimony  Powell 26, Warsh 0
Date range: 2018-01-31 to 2026-08-28
Total words in corpus: 1,342,817
```

That total — 1.34 million words across 311 documents — is also the moment it became clear that running FinBERT (a full deep-learning model) over every sentence in this corpus was going to be the single most time-consuming step in the pipeline, which is exactly what played out in [Step 9](09-tone-scoring-finbert.md).

**Next:** [Step 8 — Tone Scoring: Word List](08-tone-scoring-word-list.md).
