# Step 11: Master Dataset & Regressions (Table 3)

With tone scores from both methods ([Step 8](08-tone-scoring-word-list.md), [Step 9](09-tone-scoring-finbert.md)) and market changes ([Step 10](10-event-study.md)) all sitting in separate files, this step merges everything and runs the assignment's core statistical test.

## `src/build_master_dataset.py`

**What it does:** a straightforward merge of four tables — the corpus metadata, the word-list scores, the FinBERT scores, and the event-window changes — joined on date and document type into one 311-row, 34-column table.

**Why it's a separate script rather than inline in the regression script:** the merged table is reused by *three* later things — the regressions in this step, [Figure 1 and Table 2](12-figures-tables-and-decisions.md), and the [forecast model](13-the-forecast-model.md) — so building it once and saving it (`data/processed/master_dataset.parquet`) avoids three slightly-different re-implementations of the same join logic.

## `src/run_regressions.py`

**What it does:** implements Table 3 — regressing each of the four indicators' one-day change on each method's tone score(s), controlling for the 3-month-bill change. Following "Parsing the Fed"'s own table structure (confirmed in [Step 2](02-reading-the-research-papers.md)), each method's scores go into **one regression together**, not separate univariate regressions per score — e.g., the word-list regression for a given indicator includes all four topic scores (`wl_interest_rate`, `wl_economy`, `wl_job_market`, `wl_sentiment`) plus the control, in a single OLS model. This runs on two corpora: **statements only** (n=73, matching both readings' focus — statements are the cleanest "main event" for this kind of design) as the primary result, and a **pooled** version across statements+minutes+press-conferences (n=207) as our own extension beyond what either reading attempted. Standard errors are HC1 (heteroskedasticity-robust) throughout.

**Why controlling for the 3-month bill specifically:** the 3-month bill's own yield moves mechanically with *the rate decision itself* — it's short-duration enough to track the current/near-term fed funds rate closely. Without this control, a regression of "did the market move" on "was the language hawkish" would end up crediting the *words* for a market reaction that was actually just the *decision itself* (a hike moves short rates regardless of how it's described). This control is what lets us claim we're measuring the incremental effect of phrasing, not just re-discovering that decisions move markets.

## A bug caught before it reached the forecast

The regression output originally only saved each tone regressor's coefficient — not the model's intercept or the control variable's own coefficient. That was fine for reading Table 3 on its own, but [Step 13](13-the-forecast-model.md)'s forecast needed the fitted intercept to produce a real predicted *level* of change (not just an incremental tone effect with no baseline). We caught this while writing the forecast step, came back, and added `const` and the control column to the saved output — a small, one-line fix (`for reg in ["const", CONTROL] + regressors`), but one that would have silently produced a wrong (intercept-less) forecast if missed.

## The finding this step actually surfaced — and why it mattered

Running the regressions, something jumped out immediately: the R² for the 1-year Treasury indicator was **nearly identical (~30%) across all four different tone-scoring methods** — word list, factor similarity, FinBERT sentiment, and segmented FinBERT sentiment all landed within a point or two of each other. That's suspicious on its face: four unrelated tone measures shouldn't explain the *same* amount of variance unless something else is doing the real work. Checking the control variable's own coefficient confirmed it: **the DGS3MO control's coefficient was ≈0.8–0.9 and highly significant (p<0.0001) in every single model.** The 3-month bill and the 1-year yield simply move together on the same days, for reasons that have nothing to do with how a statement was worded — and once that's accounted for, most of the individual tone coefficients were **not** statistically significant at conventional levels (the one clear exception: word-list Interest Rate tone was significant for DXY, at p=0.030).

This is not a disappointing result to bury — it is *exactly* the confound the assignment's control is designed to catch, caught in the act, with the receipts to show it. Reporting it plainly (rather than only showing the headline R² numbers) is what makes Table 3's writeup in the final report honest science rather than a cherry-picked highlight reel.

## Result

`data/processed/table3_regressions.csv` — 16 rows (4 methods × 4 indicators) for the statements-only corpus, doubled for the pooled extension. This fed directly into the report's Table 3 (see [Step 15](15-pdf-report-generation.md)) and the "how our results compare to the readings" discussion, where our modest, mostly-insignificant net-of-control effect sizes were shown to be consistent with — not worse than — the readings' own reported numbers.

**Next:** [Step 12 — Figures, Tables & Rate Decisions](12-figures-tables-and-decisions.md).
