# Evaluating the Impact of FOMC Communications on Asset Prices

FRE-GY 7871A, NLP and the Investment Process — Assignment 2

## Aim

Kevin Warsh became Fed Chair in May 2026, succeeding Jerome Powell. This project asks three questions: **has the tone of Fed communication changed** since the handover, **does that tone actually move markets**, and **what does both of those tell us about the September 15–16, 2026 FOMC meeting** — a genuine ex-ante forecast, since that meeting's outcome is announced after this project's deadline.

We build on three assigned readings, most directly "Parsing the Fed" (a prior project using the same 4 market indicators and the same 3-method tone-scoring comparison we implement here), extending its pipeline to a longer window (Feb 2018 – Aug 2026), more document types, an explicit Powell-vs-Warsh comparison, and the forecast it didn't attempt.

## Methods applied

- **Data collection:** every FOMC statement, minutes set, press-conference transcript, Chair speech, and testimony from Feb 2018–Aug 2026, scraped directly from federalreserve.gov (311 documents total, zero extraction failures). Market data (DXY, 10s2s spread, 1-year Treasury, Growth-minus-Value spread, plus a 3-month-bill control) from Yahoo Finance and FRED.
- **Tone scoring, 3 independent methods:** a hand-built hawkish/dovish phrase lexicon; FinBERT-embedding cosine similarity to two anchor sentences ("factor similarity"); and FinBERT sentiment classification (whole-document and 3-segment versions).
- **Event study:** one-day market-reaction windows around every release, computed two ways (a time-aware primary window and a fixed secondary window matching the reading's convention).
- **Regression:** each indicator's one-day change regressed on each method's tone score(s), controlling for the change in the 3-month T-bill — so market reactions get credited to *how* something was said, not *what* was decided.
- **Forecast:** a from-scratch, text-based rate-decision classifier feeding an ordinal logistic regression, cross-checked against real market pricing (CME FedWatch, Kalshi, Polymarket) found via live research.

## Key results

- **A real, concrete hawkish pivot:** Powell's Fed cut rates six meetings in a row (mid-2025 – April 2026); Warsh then **held** at his first meeting (June 2026) and **hiked** at his second (July 2026) — found by classifying every statement's decision directly from its own text.
- **A confound, caught and correctly handled:** the 1-year Treasury regression showed ~30% R² across all four tone methods — nearly identical, which was suspicious. Checking the control confirmed the 3-month bill was doing almost all the work (coefficient ≈0.8–0.9, p<0.0001); net of that, most individual tone coefficients were *not* statistically significant. This is exactly the confound the assignment's control is designed to catch.
- **External validation we didn't expect:** real market pricing in early September 2026 independently priced the meeting as a "coin flip," driven by the same catalyst (Warsh's Aug 28 Jackson Hole speech) our text-only model flagged on its own — a strong, unplanned cross-check.
- **Final forecast:** P(cut) ≈ 5%, P(hold) ≈ 35%, P(hike) ≈ 60% — blending our model's raw output (72.7% hike, likely overconfident given a 68-meeting training set) with the market cross-check rather than reporting either alone.
- **A bug found and fixed post-delivery:** minutes were originally assigned the meeting date as their release date instead of their true ~3-week-later publication date, silently duplicating that day's statement reaction onto the minutes row. Caught by a user question, fixed, and verified to leave the primary (statements-only) results and the forecast completely unchanged — see Step 17 below and `AI_USE.md`.

## How this was built — the story, compressed

*(This is a condensed version of `docs/STORY.md`, which has a fuller step-by-step account with more detail per step. Every code file in `src/` is covered below.)*

**1–2. Understanding the assignment & reading the papers.** No code — verified via web search that Warsh's Fed-chair tenure is a real, recent event (postdates training data), not a hypothetical, and pinned down the exact 2026 timeline before writing anything. Read all three assigned papers in full and found "Parsing the Fed" was structurally a prior version of this exact assignment, letting us reuse its exact formulas rather than inventing our own; also found the deeper Doh et al. method is structurally inapplicable to recent data (5-year declassification lag on the Fed's internal "alternative statements").

**3. Environment & repo setup.** Checked Python 3.14 had no PyTorch wheel yet before committing to it, used 3.13 instead. `.gitignore` and `.env` (holding the FRED key) were created before `git init`, so a credential could never accidentally get committed.

**4. Scraping FOMC core documents.** `config.py` holds every shared constant — file paths, HTTP settings, and the full verified list of every FOMC meeting date 2018–2026 (pulled directly from the Fed's own calendar pages, not typed from memory). `scrape_utils.py` provides shared fetch/cache/text-extraction helpers reused by every scraper. `scrape_fomc_core.py` uses both to pull every statement, minutes set, and press-conference transcript, correctly attributing each to Powell or Warsh (including the narrow chair-pro-tempore window). **Result: 73 statements, 69 minutes, 65 press conferences, zero failures.**

**5. Scraping speeches & testimony.** `scrape_speeches_testimony.py` finds every Fed speech/testimony page by speaker surname in the URL, then filters to each person's *actual tenure as Chair* — a Powell speech after May 15, 2026 is excluded even though he remained a Governor and kept speaking. **Result: 78 speeches, 26 testimony documents, zero failures.**

**6. Collecting market data.** `fetch_market_data.py` pulls DXY/IWF/IWN from Yahoo Finance and T10Y2Y/DGS1/DGS3MO from FRED, computing Growth-minus-Value as a return spread (not a price-level difference) per the assignment's own definition. **Result: a 2,270-row daily panel, Jan 2018–Sept 2026.**

**7. Building the corpus.** `build_corpus.py` merges both scrapes into one table and computes each document's release hour — the detail that later decides which market-close window is the correct one to measure. **Result: `corpus.parquet`, 311 rows, 1.34M words total.** *(Post-delivery fix: this script now also computes a separate `release_date_dt`, since minutes' identifying date and true publication date differ by ~3 weeks — see Step 17.)*

**8. Tone scoring — word list.** `text_utils.py` provides sentence splitting; `lexicon.py` is our hand-built ~100-phrase hawkish/dovish lexicon (topic-tagged: interest rate, economy, job market, sentiment); `tone_word_list.py` implements the reading's exact sign-aggregation scoring formula. Sanity-checked against known-tone statements (March 2020 emergency cuts scored -1.0, 2022 hiking-cycle statements scored +1.0) before trusting it on the full corpus.

**9. Tone scoring — FinBERT.** `tone_finbert.py` loads FinBERT once and computes both the factor-similarity scores (cosine similarity to "Inflation will rise" / "Interest rates will rise") and sentiment scores (P(positive), whole-document and 3-segment) from the same forward pass. Benchmarked CPU vs. Apple GPU first — CPU won (0.07s vs 0.21s per batch), a real, counterintuitive finding for a model this size. **Result: 311 documents scored in 12m55s.**

**10. Event study.** `event_study.py` computes the one-day change in all four indicators (plus the control) around every release, two ways: a time-aware primary window and a fixed secondary window for direct comparability with the reading. Handles the fact that equities/FX and Treasuries don't share an identical holiday calendar. **Result: zero missing values across all 311 documents.** *(Originally anchored windows on each document's identifying date; this had a real bug for minutes, corrected in Step 17 — see below.)*

**11. Master dataset & regressions.** `build_master_dataset.py` merges everything into one table; `run_regressions.py` implements Table 3, regressing each indicator on each method's score(s) jointly, controlling for the 3-month bill. This is where the DGS3MO confound described above was caught.

**12. Figures, tables & rate decisions.** `make_figure1.py` builds the 3-panel tone-over-time chart; `make_table2.py` isolates the Warsh-era releases; `rate_decisions.py` classifies every statement's actual decision (cut/hold/hike) directly from its text via regex, surfacing the hold→hike pivot that became the forecast's empirical backbone.

**13. The forecast model.** `forecast.py` fits an ordinal logistic regression for rate-decision probabilities, estimates statement-tone momentum (catching and explaining a ceiling effect in the naive estimate), and converts Table 3's regression coefficients into market-reaction probabilities. A live web search for real market pricing provided the external cross-check described above.

**14. Notebook assembly.** `notebooks/analysis.ipynb` — built cell by cell, loading each script's saved output rather than re-running the full ~15–20 minute pipeline inline, then executed top-to-bottom and verified programmatically to have zero cell errors.

**15. PDF report generation.** `generate_report.py` builds the standalone Brightspace report as HTML (pulling every table/figure live from the same data files) and renders it via `weasyprint`. Two rounds of layout fixes: wide tables moved to landscape orientation, then Table 3 split into four per-method tables after the giant single-table version proved sparse and prone to page-break artifacts.

**16. Finalizing & shipping.** `AI_USE.md` rewritten with a specific account of what was AI-generated vs. jointly decided; `PLAN.md` closed with an appended execution log rather than rewritten history; verified via `git ls-files` that no data or secrets were ever committed.

**17. Post-delivery bug fix: minutes' release date.** After shipping, a user question about the regression design ("what if two documents release at the same time?") led to checking whether event-study windows actually used each document's *real* release date. They didn't for minutes — the original code used the meeting date, but minutes actually publish ~3 weeks later, so every minutes row in Table 2 was silently duplicating that day's statement reaction. Fixed in `scrape_fomc_core.py` (computes the true release date using the Fed's own stated "three weeks after the decision" policy, verified against 5 independently-confirmed real dates spanning 2018–2026 — an initial attempt at scraping the page's own "Last Update" field was tried and rejected after it disagreed with a verified real date by 44 days), `build_corpus.py` (carries a new `release_date_dt` field alongside the unchanged identifying `date`), and `event_study.py` (anchors windows on the corrected field). Verified after the fact, not just assumed: the statements-only Table 3 result and the forecast are byte-for-byte identical before and after the fix, since neither ever used minutes data — only Table 2's minutes rows and Table 3's pooled extension actually changed. Full blast-radius plan in `PLAN.md` Section 9.

## Repository structure

```
src/            18 pipeline scripts (see above)
notebooks/      analysis.ipynb — the executed deliverable notebook
docs/           STORY.md + 17 step-by-step build docs (fuller version of the story above)
data/           gitignored — regenerate by running src/ scripts in dependency order
report/         gitignored — the Brightspace PDF, generated by src/generate_report.py
PLAN.md         the working plan, written before execution, plus an appended execution log
AI_USE.md       AI use disclosure
```

## Setup

```bash
python3.13 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

Create a `.env` file in the repo root with:

```
FRED_API_KEY=your_key_here
```

(free, instant signup at https://fred.stlouisfed.org/docs/api/api_key.html)

## Data sources

- Fed statements, minutes, speeches/testimony/press-conference transcripts: federalreserve.gov
- DXY, Russell 1000 Growth (IWF), Russell 2000 Value (IWN): Yahoo Finance
- 10s2s spread (T10Y2Y), 1-year Treasury (DGS1), 3-month T-bill (DGS3MO): FRED

## Further reading

- **`docs/STORY.md`** — the full, linked, step-by-step build narrative (this README is a compressed version of it)
- **`PLAN.md`** — methodology decisions and rationale, written before execution, with an execution log appended after
- **`AI_USE.md`** — how AI assistance was used, specifically
