# Step 12: Figures, Tables & Rate Decisions

Three small, focused scripts — but one of them surfaced the single most important finding used in the final forecast.

## `src/make_figure1.py`

**What it does:** builds Figure 1 — three stacked panels (one per tone-scoring method: word-list Interest Rate score, factor-similarity rate score, FinBERT sentiment), each a scatter plot of every document's score over time, colored by document type, with a vertical dashed red line marking Warsh's swearing-in (May 22, 2026). Saved as a PNG rather than left as a live matplotlib object, so it could be embedded both in the notebook and, later, the PDF report without needing to regenerate it twice.

**Why three stacked panels rather than one combined chart:** the assignment asks for tone "over time by document type," and showing all three methods side by side (rather than picking one as "the" tone measure) is what makes the later multi-method comparison possible — a reader can see immediately where the methods agree and where they don't, which turned out to matter (see [Step 13](13-the-forecast-model.md), where the word-list and FinBERT sentiment scores actually *disagree* on direction for one key comparison).

**Result:** `notebooks/figure1_tone_over_time.png` — a clean, dated view of 8.5 years of Fed communication tone across three independent measurement methods, with the Warsh-era documents visibly clustered at the right edge of the timeline (a reminder, visually, of exactly how small that sample is).

## `src/make_table2.py`

**What it does:** filters the master dataset down to just the 7 Warsh-era documents and lays out every one of their tone scores next to their market-reaction numbers, in the exact shape the assignment's Table 2 requires.

**Why a separate, tiny script rather than just a notebook cell:** keeping it as a standalone script means it can be re-run independently any time the underlying scores or event-study numbers change upstream, without needing to re-execute the whole notebook — useful during the iterative bug-fixing that happened in [Step 11](11-master-dataset-and-regressions.md) and [Step 13](13-the-forecast-model.md).

**Result:** `data/processed/table2_warsh_era.csv`, 7 rows. One genuinely interesting detail visible in it: the June 2026 press conference scored **-1.0** (fully dovish) on `wl_interest_rate` even though the *statement* released the same day scored 0.0 (neutral) — a real divergence between the formal written statement and the more conversational Q&A, which is exactly the kind of nuance that tracking multiple document types (not just statements) is meant to surface.

## `src/rate_decisions.py`

**What it does:** classifies every one of the 69 regular-meeting statements as a **cut**, **hold**, or **hike** — directly from the statement's own text, using three simple regex patterns looking for "raise"/"raising," "lower"/"lowering," or "maintain" next to "the target range for the federal funds rate." This was deliberately chosen over trying to parse the exact numeric rate range out of the text (which uses inconsistent fraction notation across the years, like "3-1/2 to 3-3/4") — the verb next to "target range" turned out to be a far more robust signal, confirmed by checking it against both a 2018 and a 2026 statement during the original scraping reconnaissance in [Step 4](04-scraping-fomc-core-documents.md).

**Why this needed to be built at all:** the forecast in [Step 13](13-the-forecast-model.md) needed real historical decision data to learn from — "does hawkish language tend to precede a hike?" can't be answered without a ground-truth series of what actually happened at each meeting. Rather than manually looking up 69 Fed decisions or trusting a possibly-stale external dataset, extracting it directly from documents we'd already scraped and already trusted was both more reliable and required no new data source.

## Result — the finding that shaped the whole forecast

The classifier ran cleanly across all 69 meetings with **zero unclassifiable statements**. The output showed:

```
hold: 37   hike: 17   cut: 15
```

And, most importantly, the tail end of the series:

```
20250618  hold      20260128  cut
20250730  cut       20260318  cut
20250917  cut       20260429  cut
20251029  cut       20260617  hold   <- Warsh's first meeting
20251210  cut       20260729  hike   <- Warsh's second meeting
```

Powell's Fed was cutting steadily from mid-2025 through April 2026 — six cuts in a row. Then Warsh **held** at his very first meeting and **hiked** at his second. This is a real, concrete, hawkish pivot exactly at the leadership transition — not a subtle statistical artifact, but a plainly visible change in actual policy direction — and it lines up with the hawkish word-list and FinBERT tone scores on those same two statements found back in [Step 8](08-tone-scoring-word-list.md). This single table became the empirical backbone of the entire forecast in the next step.

**Next:** [Step 13 — The Forecast Model](13-the-forecast-model.md).
