# Step 17: Post-Delivery Bug Fix — Minutes' Release Date

Everything through [Step 16](16-finalizing-and-shipping.md) had already shipped — code pushed, notebook executed, PDF delivered — when this correction happened. It gets its own chapter rather than a silent edit to the earlier steps, because that's what actually occurred and this project's whole documentation practice has been to record what happened, not a tidied-up version of it.

## How it was found

The user asked a methodological question about the regression design: "is there one document per market effect? what if there are say 2 documents released at the same time?" Answering that properly — rather than in the abstract — meant actually checking whether the event-study code used each document's *true* release date. It didn't, for one document type.

## The bug, precisely

`scrape_fomc_core.py`'s `scrape_minutes()` stored the *meeting* date (e.g. `20260729`) as a minutes document's only date field, because that's the date embedded in the Fed's URL for minutes pages. `event_study.py` read that field directly as "when was this released." But FOMC minutes are not published on the meeting date — they come out roughly three weeks later. The practical effect: every minutes document's computed "market reaction" in Table 2 was actually a second copy of that day's statement/press-conference reaction, mislabeled as the minutes' own effect.

## Verifying the fix mechanism before writing it — and catching a second, subtler mistake along the way

The first instinct was to scrape the minutes page's own `id="lastUpdate"` div (e.g. "Last Update: August 19, 2026") as the true publication date. Before trusting that, it was checked against three real minutes pages spanning 2018–2026 — all three matched the well-known ~3-week convention (21–22 day gaps).

That felt like enough, until a wider check was run across all 69 minutes documents and one showed a 65-day gap: the September 21–22, 2021 meeting's `lastUpdate` read "November 26, 2021." An independent web search confirmed the *real* release date was October 13, 2021 — 44 days off from what the page's own `lastUpdate` field claimed. The `lastUpdate` field, it turned out, reflects whenever a page was last technically touched — which can be a much later, unrelated edit (a correction, an accessibility fix, a template change) — not necessarily the original publication moment.

So the fix was revised again before shipping: instead of trusting a scraped field, it computes the release date directly from the Fed's own consistently and publicly stated policy — "minutes... ordinarily are made available three weeks after the day of the policy decision" — and verified that computed rule against **5 independently confirmed real release dates** spanning the full 2018–2026 window, including a December/holiday-season meeting (Dec 19, 2018 → Jan 9, 2019, an exact match even across the holidays). The scraped `lastUpdate` field is kept only as a diagnostic cross-check, printed as a warning if it disagrees with the computed date by more than 3 days — which happened for exactly one document (the 2021 one already found), and zero others across all 69 minutes.

## The plan, written before any code changed

Per the user's explicit request to be "super super cautious about the blast radius," a full plan was written into `PLAN.md` Section 9 *before* touching any code — tracing exactly which files needed to change (3: `scrape_fomc_core.py`, `build_corpus.py`, `event_study.py`), which data artifacts needed regenerating, and — critically — which artifacts and numbers were mathematically guaranteed *not* to change and why (the ~13-minute FinBERT tone-scoring run, the statements-only Table 3 regression, and the entire forecast, none of which ever depended on minutes' event-study data).

## The fix

- **`scrape_fomc_core.py`**: `scrape_minutes()` now computes `actual_release_date` via the verified 21-day rule, cross-checks it against `lastUpdate`, and stores both — leaving the original `date` field (the meeting date, used as the cross-table join key everywhere else) completely untouched.
- **`build_corpus.py`**: parses `actual_release_date` into a new `release_date_dt` column, defaulting to the existing `date_dt` for every document type where the two are already identical (everything except minutes).
- **`event_study.py`**: anchors its window lookups on `release_date_dt` instead of `date_dt` — a one-line change, identical logic otherwise.

## Result — verified, not assumed

Re-running the pipeline in dependency order:
- The scraper re-parsed all 69 minutes pages from cache (no new network calls) and printed exactly **one** cross-check warning — the already-known 2021 case — confirming the 21-day rule held for the other 68 without needing individual verification.
- `build_corpus.py` reported **exactly 69 documents** where `release_date_dt` differs from the identifying date — precisely the minutes count, confirming the fix touched nothing else.
- `event_study.py` still showed **zero missing values** across all 311 documents after the fix.
- Table 2's Warsh-era minutes rows now show genuinely different numbers from that day's statement/press-conference (e.g. the July 2026 minutes: `d_1yr = 0.01`, vs. the July 2026 statement/presser's `d_1yr = -0.05` — different market days, different numbers, as they should be).
- Table 3's **statements-only** regression coefficients were checked against the pre-fix values and came back **byte-for-byte identical** (e.g. word-list 1yr-Treasury R² = 0.322202, unchanged to six decimal places) — confirming this regression never depended on minutes data, exactly as predicted before the fix was written.
- `forecast.py`'s output was re-run and also came back **byte-for-byte identical** (P(hike) = 72.7%, same market-reaction predictions) — confirming the forecast section of the report stands as originally delivered.
- The notebook was re-executed top to bottom: still **20 cells, zero errors**.
- The PDF report was regenerated and visually spot-checked: Table 2's minutes rows now correct, Table 3 unchanged.

## What actually changed in the deliverables, and what didn't

**Changed:** Table 2's two minutes rows (now showing their real, ~3-week-later market reaction); Table 3's pooled (statements+minutes+press-conferences) extension, which is explicitly labeled as *our* extension beyond the readings, not the report's primary result.

**Did not change:** Table 3's primary statements-only regression, the DGS3MO-confound finding, the "Parsing the Fed" benchmark comparison, the rate-decision classifier, and every number in the forecast section — none of these ever touched minutes' event-study data.

## Documentation updated to match

`AI_USE.md` gained a dedicated section owning this as a mistake in the original implementation, not a vague "improvements were made" note. `README.md`'s Steps 7 and 10 summaries and Key Results section were updated, and this file was added as Step 17. `docs/steps/04`, `10`, and `12` each got a correction note left visible alongside the original (now-corrected) text, rather than a silent rewrite — consistent with how this whole documentation set has tried to represent what actually happened, mistakes included.

This wasn't the last correction either — see [Step 18](18-forecast-redesign.md), a more conceptual fix to the forecast model itself, found shortly after this one.

**Next:** [Step 18 — Forecast Redesign](18-forecast-redesign.md). **Back to:** [the central index](../STORY.md).
