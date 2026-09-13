# Assignment 2 — Master Plan
FRE-GY 7871A, NLP and the Investment Process — "Evaluating the Impact of FOMC Communications on Asset Prices"

Status: **DRAFT v2 — for discussion.** This is a living document. We update it as we make decisions; nothing below gets executed until we've agreed on it step by step.

**v2 changelog:** all three readings received and fully read; GitHub repo URL received (https://github.com/Aditya-Gupta26/FRE-GY_7871A_Assignment_2); FRED key in progress. Section 1, Section 3 (new 3A), and Step 3/4 of Section 5 substantially revised with concrete formulas now that we've seen the actual papers instead of guessing at them.

---

## 0. Critical facts to internalize before anything else

These came from web research done *for this planning session*, because they postdate general training knowledge and the whole assignment hinges on getting them right.

| Fact | Value | Source |
|---|---|---|
| Powell's last day as Chair | May 15, 2026 (stayed as "chair pro tempore" briefly after) | [Fed press release](https://www.federalreserve.gov/newsevents/pressreleases/other20260515a.htm) |
| Warsh confirmed by Senate | May 13, 2026 (54–45) | [NPR](https://www.npr.org/2026/05/13/nx-s1-5816235/kevin-warsh-federal-reserve-chair-jerome-powell) |
| **Warsh sworn in as Chair** | **May 22, 2026** | [Fed press release](https://www.federalreserve.gov/newsevents/pressreleases/other20260522a.htm) |
| Warsh's first FOMC meeting as Chair | **June 16–17, 2026** | [Fed](https://www.federalreserve.gov/monetarypolicy/fomcpresconf20260617.htm) |
| Second Warsh-era meeting | July 28–29, 2026 | search results |
| **Next FOMC meeting (the one we forecast)** | **Sept 15–16, 2026** | multiple sources |
| Today | **Sept 12, 2026** | system clock |
| Assignment due | Tuesday night, **Sept 15, 2026, midnight** | assignment PDF |

**Three consequences that shape the whole plan:**

1. **We have only ~3 days.** This is the single biggest constraint on scope. "Thorough and cautious" has to mean *thorough about what matters, ruthless about what doesn't* — not exhaustive data collection across 300+ documents with three NLP methods each polished to perfection. I'll flag scope trade-offs explicitly at each step so we can consciously choose where to spend the limited time.
2. **The Warsh era is tiny by construction** — 2 FOMC statements, 2 sets of minutes (assuming July minutes are out — need to check), and whatever speeches/testimony he's given since May 22. Table 2 ("each Warsh-era release") will have on the order of 5–15 rows, not dozens. This isn't a flaw in our approach — it's the actual shape of the data — but Table 3's regression must be run on the **full Powell+Warsh pooled sample** (needs the N), not Warsh-only, or it'll be statistically meaningless. This is a decision we lock in now (Section 5, Step 3).
3. **The forecast is genuinely ex-ante.** The Sept 15–16 meeting's outcome is announced *after* our deadline. We cannot "check the answer." This is good — it means the forecasting step is real, not theater — but it also means our probabilities should be defensible from the model, not reverse-engineered from a known outcome.

---

## 1. Restating the task, in plain terms

Warsh has been Chair for under 4 months. The assignment wants us to:

1. **Build a corpus** of Fed communications (statements, minutes, Chair speeches/testimony/press-conference transcripts) from Feb 2018 (Powell's start) to today.
2. **Score each document's hawkishness/dovishness** two-plus ways (a hand-built word list, and a language model like FinBERT), and track how tone has moved — especially: did it shift materially when Warsh took over vs. the Powell trend?
3. **Check whether tone actually moves markets** — regress the one-day move in 4 market indicators on the tone score, controlling for the 3-month T-bill move (so we're crediting the *words*, not the *rate decision itself*, which also moves the 3-month bill).
4. **Use both of the above to forecast** the Sept 15–16, 2026 meeting: rate decision probabilities, whether the statement will be more hawkish than July's, expected market reaction, and a trade recommendation with a stated falsification condition.

The explicit ask to "build on" and "compare against" three specific readings (Doh/Kim/Yang 2021, Doh/Song/Yang 2020/2023, and the "Parsing the Fed" deck) matters a lot: the four market indicators in the assignment are **exactly** the four used in "Parsing the Fed," and that deck compares three tone-scoring methods (factor/embedding similarity, word list, FinBERT sentiment). This is not a coincidence — the assignment is explicitly a mini-replication of that research line. That should raise our ambition from "two methods, minimally" to **three methods**, since it costs little extra and directly enables the required comparison-to-readings discussion.

**Now that we've read all three papers, here's what "building on their methods" concretely means** (full detail in new Section 3A below):

- **"Parsing the Fed" is the direct template.** It's not a peer-reviewed paper — it reads as a prior course project — and it is structurally almost identical to this assignment: same 4 indicators, same 3 tone-scoring methods, same regression-based validation. We are extending its pipeline (longer window, more document types, Powell-vs-Warsh, forecast) rather than inventing our approach from scratch.
- **Doh, Kim & Yang (2021)** and **Doh, Song & Yang (2020/2023)** score tone by comparing each official statement's embedding against the Fed's own internally-drafted "alternative statements" (dovish Alt A / consensus Alt B / hawkish Alt C-D) — but those are **only declassified after a 5-year lag**, so as of today they only exist through roughly mid-2021. That makes their exact method structurally inapplicable to the Warsh era or to our forecast, which is an important, honestly-stated limitation for the report rather than something to paper over.

---

## 2. Requirements checklist (exhaustive, pulled directly from the rubric)

Use this as the source of truth for "did we miss anything." Nothing gets marked done here without an artifact to point to.

### Data
- [ ] Press releases (post-meeting statements), Feb 2018 → today
- [ ] Meeting minutes, Feb 2018 → today
- [ ] Chair's speeches, testimony, and press-conference transcripts, Feb 2018 → today
- [ ] Every document has a recorded **release date and time**
- [ ] DXY (Yahoo `DX-Y.NYB`)
- [ ] 10s2s spread (FRED `T10Y2Y`)
- [ ] 1-year Treasury yield (FRED `DGS1`)
- [ ] Growth minus value = Russell 1000 Growth return − Russell 2000 Value return (Yahoo `IWF` − `IWN`)
- [ ] 3-month T-bill yield (FRED `DGS3MO`) — control variable only

### Analysis
- [ ] ≥2 tone-scoring methods (word list + LM); we're targeting 3 (+ embedding similarity)
- [ ] Tone tracked over time, broken out **by document type**
- [ ] Explicit Warsh vs. Powell comparison
- [ ] One-day change computed for all 4 indicators around **every** release
- [ ] Regression of each indicator's one-day change on each tone score, **controlling for ΔDGS3MO**
- [ ] Forecast section uses steps 2 & 3 as inputs (not vibes)

### Forecast (must appear, with these exact shapes)
- [ ] Rate decision: P(cut) + P(hold) + P(hike) = 100%
- [ ] P(Sept statement more hawkish than July statement)
- [ ] For each of the 4 indicators: P(rises on announcement day) + expected magnitude
- [ ] One recommended position, the reasoning, and an explicit "this would prove me wrong" condition

### Deliverable 1 — GitHub repo
- [ ] Viewable link (public, or private+shared — decide in Section 4)
- [ ] Notebook, **run top-to-bottom with output saved/rendered**
- [ ] Supporting code
- [ ] `AI_USE.md` completed
- [ ] **No data files committed** (raw scrapes, price CSVs, model weights all excluded)

### Deliverable 2 — PDF report (Brightspace)
- [ ] Table 1: documents collected, by type × by Chair
- [ ] Figure 1: hawkish/dovish tone over time by document type, **Warsh start date marked**
- [ ] Table 2: one-day indicator changes after each Warsh-era release, next to that release's tone scores
- [ ] Table 3: regression of each indicator's change on each tone score, with 3-month-bill control
- [ ] Written comparison of our methods/results vs. the three readings
- [ ] Forecast + recommendation (same content as above, written up)

---

## 3. Decisions already made (and why)

| Decision | Rationale |
|---|---|
| Use **3 tone-scoring methods**: hand-built hawkish/dovish word list, FinBERT sentence-level sentiment, and embedding cosine-similarity to hawkish/dovish anchor sentences | Assignment only requires 2, but "Parsing the Fed" uses exactly these 3, and the assignment reuses that paper's 4 indicators verbatim — strongly implies we're meant to be comparable to it. Marginal cost of the third method is low once the pipeline exists. |
| Regression (Table 3) runs on the **full pooled Powell+Warsh sample**, not Warsh-only | Warsh-only N is ~2–15 depending on doc type — regression coefficients on that would be noise. Table 2 is where Warsh-only granularity belongs (it's just a data table, not an inferential claim). |
| Word-list scoring is **phrase-based, topic-tagged, sign-aggregated** per the "Parsing the Fed" formula (Section 3A), not unigram counts | The assignment's own example — "higher inflation" (hawkish) vs. "inflation has eased" (dovish) — shows the word "inflation" alone carries no signal; direction comes from the modifier. A unigram bag-of-words dictionary would misscore this immediately, and we now have an exact precedent formula to implement instead of inventing one. |
| Factor-similarity method uses **FinBERT embeddings + the exact two anchors from "Parsing the Fed"** ("Inflation will rise", "Interest rates will rise"), not a generic sentence-transformer or invented anchor set | Matches the template precisely, which is what makes the comparison-to-readings section meaningful rather than approximate. |
| Event window for "one-day change" has **two versions**: (primary) same-day close-to-close if released before the 4pm ET close, next-trading-day close-to-close if released after; (secondary, for direct comparability with "Parsing the Fed") their fixed **prior-day-close → next-day-close** symmetric 2-day window | The assignment explicitly asks us to record release *time*, which "Parsing the Fed" didn't bother doing — they used a blanket symmetric window regardless of time of release. Our time-aware version is a genuine methodological improvement worth calling out in the comparison section; keeping their version too lets us sanity-check that our refinement doesn't produce wildly different numbers. |
| Table 3 regressions are **multi-regressor per method** (all of a method's scores as simultaneous regressors in one model per indicator, plus the ΔDGS3MO control), not one univariate regression per score | This is what "Parsing the Fed"'s own result tables actually show (e.g., `rate_score` and `inf_score` together in one regression). Matches precedent and avoids needlessly throwing away information from correlated same-method scores. |
| Table 3's primary corpus is **statements only** (both readings' main focus), with the full pooled multi-type sample (statements+minutes+speeches+press-conferences) as a clearly-labeled extension beyond what either reading did | Neither reading mixed document types into one regression; statements are also the cleanest "main event" for an event-study design. Pooling everything is *our* contribution, and should be presented as such rather than implied to be standard practice. |
| Sept 15–16 meeting forecast will **not** reference the actual outcome | Structurally impossible anyway (decision announced after our deadline), but worth stating as a principle: the forecast must be defensible from Steps 2–3 alone, cross-checked against public market-implied pricing (e.g., CME FedWatch) as an external sanity check — not derived from it. |

---

## 3A. Exactly what we're borrowing from each reading

This replaces guesswork from v1 with the actual formulas/approaches from the papers, mapped to what we'll implement.

### From "Parsing the Fed" (our primary template)

**Method 1 — Factor similarity.** Embed document sentences with **FinBERT** (not a generic sentence encoder). Define two one-sentence "factor" anchors: **"Inflation will rise"** and **"Interest rates will rise."** For each document, compute the average cosine similarity of its sentence embeddings to each anchor separately → two scores per document, `inf_score` and `rate_score`. Regress each of the 4 indicators on **both scores together** in one model (not two separate univariate regressions) — this is what their results table actually shows (one regression per indicator with `rate_score` and `inf_score` as simultaneous regressors). We'll add our ΔDGS3MO control on top, since their version didn't need one (they weren't isolating language from decision).

**Method 2 — Word list / phrase lexicon.** A **handcrafted lexicon of phrases** (not single words), each phrase tagged with a **topic** (their example topics: Interest Rate, Economy, Job Market, plus a general Sentiment bucket) and a **sentiment score** (+1/0/−1). Words within a phrase don't need to be strictly adjacent. Per-topic document score:

  x_k(t) = (1/n_k) · Σᵢ sign( Σₚ L(p)·S(p)·1ₖ(i) )

  where the outer sum is over sentences `i` that mention topic `k` (n_k of them), the inner sum is over phrases `p` present in that sentence, `L(p)` is phrase length, `S(p)` is the phrase's hand-labeled sentiment. We'll build our own lexicon (theirs wasn't published in full, just examples), organized the same way, and regress each indicator on the topic scores jointly + our ΔDGS3MO control.

**Method 3 — FinBERT sentiment.** Baseline: run FinBERT per sentence, score = P(positive class), averaged over the whole document. Their enhancement, which measurably improved fit (R² roughly doubled on some indicators): split each document into **3 segments** (e.g., thirds by position) and score each segment separately, then regress each indicator on the 3 segment scores jointly. We'll implement the whole-document average as the required baseline, and add segment-scoring as a stretch enhancement if time allows — it's a genuine, cheap improvement per their own results.

**Benchmark numbers worth reusing directly in our report:** their Appendix table of R² by method × indicator (2011–2021 and 2016–2021 windows) gives us a concrete, citable baseline to place our own R² next to in Table 3's write-up — e.g., word list topped out around 24–34% R² on 1-year Treasury and Growth-Value spread; factor similarity did best on Growth-Value (~22–24%); FinBERT sentiment was weaker (~11–15%) until segment-scored. If our numbers land in a similar range, that's a meaningful validation; if not, that's worth discussing too.

### From Doh, Kim & Yang (2021) and Doh, Song & Yang (2020/2023)

Their core method (Universal Sentence Encoder similarity to the Fed's internal dovish/hawkish "alternative statements," combined with a novelty term into a "Stance" measure, and decomposed into expected-vs-surprise using intraday bond futures) is **not directly implementable for current data** for two structural reasons already noted: (1) alternative statements are undisclosed for ~5 years, so unavailable for anything after ~2021; (2) their surprise-decomposition requires intraday tick data we don't have. Given the ~3-day timeline, we will **not** attempt a full replication of this method as a fourth core method. Instead:

- We cite their approach and formulas in the report's comparison section as the theoretically richer benchmark our simpler methods are approximating.
- **Optional stretch, only if time allows after everything else is done:** apply the alternative-statement-similarity idea to just the 2018–2021 subset of Powell statements where alternative statements are actually declassified, as a small bonus validation exercise showing we understand the deeper method even though we can't run it on Warsh-era data. Not committed to — revisit only after Steps 0–6 are solid.
- We adopt their explicitly-stated principle of **isolating language from decision** (their MPS = stance minus expected stance) as the intellectual justification for why *our* Table 3 controls for ΔDGS3MO — same goal, cheaper implementation.

---

## 4. Things I need from you before/while we execute

Updated — item 1 (readings) is resolved; item 2 (repo) is resolved. Remaining:

1. ~~The three readings~~ — **done**, received and read; see Section 3A.
2. ~~GitHub repo~~ — **done**: https://github.com/Aditya-Gupta26/FRE-GY_7871A_Assignment_2. Need to confirm: is it currently empty, and is it public (assignment just needs "a viewable link," public is simplest)?
3. **FRED API key**: in progress on your end (fred.stlouisfed.org, free/instant). Ping me the key (or just tell me it's ready) when you have it — needed for DGS1/T10Y2Y/DGS3MO in Step 2.
4. **Time budget confirmation**: given the ~3-day window, are you able to work through this with me in a fairly compressed, back-to-back way over the next couple of days, or do we need to pre-negotiate scope cuts now (e.g., cap speeches/testimony to a curated subset rather than the full archive)? I have a proposed scope below (Section 5, Step 1) that I think is achievable, but flagging this now so we're not surprised on day 3.
5. **Local environment**: confirm Python version available (`python3 --version`) and whether you want a `venv` or `conda` env — I'll set it up once confirmed.

---

## 5. Step-by-step plan

Each step lists: **what**, **why this approach**, **how**, **output**, and **watch-outs**. We do these one at a time — I will not jump ahead without checking in.

### Step 0 — Environment & repo scaffold
**What:** Set up Python env, `requirements.txt`, folder structure, git init, `.gitignore` (excluding all data/, *.csv, model caches, API keys).
**Why:** Everything downstream depends on a working, reproducible environment; doing this first avoids "works on my machine" surprises later, and the "no data files" repo requirement is easiest to satisfy if `.gitignore` is right from commit #1 rather than retrofitted.
**How:** `venv`, core libs: `requests`, `beautifulsoup4`, `lxml`, `pdfplumber` (PDF transcripts), `pandas`, `numpy`, `yfinance`, `fredapi` (or `pandas-datareader`), `transformers` + `torch` (FinBERT), `sentence-transformers` (embedding similarity), `nltk` or `spacy` (sentence splitting), `statsmodels`, `matplotlib`, `seaborn`, `jupyter`.
**Output:** Repo skeleton (`/src`, `/notebooks`, `README.md`, `AI_USE.md` stub, `requirements.txt`, `.gitignore`), committed.
**Watch-outs:** Don't commit a populated `data/` folder even transiently; `torch`/`transformers` installs are large — confirm disk space isn't an issue.

### Step 1 — Document collection
**What:** Scrape statements, minutes, and Chair speeches/testimony/press-conference transcripts, Feb 2018 → Sept 2026, from federalreserve.gov, with release date+time.
**Why this scope:** The Fed's site has stable, date-patterned URLs across this whole window (e.g., `/newsevents/pressreleases/monetaryYYYYMMDDx.htm` for statements, `/monetarypolicy/fomcminutesYYYYMMDD.htm` for minutes, `/newsevents/speech/` and `/newsevents/testimony/` archives filterable by speaker, `/monetarypolicy/fomcpresconfYYYYMMDD.htm` linking to PDF transcripts). This is scriptable, not manual, which is the only way to hit ~330 documents in the time we have.
**Realistic volume estimate:** ~68 statements, ~65 minutes (July 2026 minutes need checking — may not be out yet), ~30 press-conference transcripts (every meeting since 2019, quarterly before), ~17 semiannual testimonies, and speeches — likely 100–200 over 8.5 years if we take every Chair speech in the archive. **Proposed scope cut given the 3-day window:** take *every* statement, minutes, testimony, and press-conference transcript (these are all clearly in-scope and manageable in count), but for speeches, filter the archive to Chair-only (Powell/Warsh) and take all of them — if that proves too large once we see the real count, we cut to monetary-policy-relevant venues only (drop purely ceremonial/community-outreach speeches). We'll check the actual archive count together before committing to the cut.
**How:** One scraper module per document type, with a shared `fetch + parse + store(date, time, doc_type, speaker, text, url)` interface; PDFs go through `pdfplumber`; polite scraping (delay between requests, respect the site, cache raw HTML/PDF locally — gitignored — so we don't re-hit the server on every rerun).
**Output:** A local (not committed) structured dataset — one row per document — that feeds Table 1 directly (group by type × chair).
**Watch-outs:** Fed site structure has had minor URL scheme changes over 8 years (older pages, pre-2020ish, sometimes differ); speech pages don't always disclose an exact release *time* (default to date-only + a documented convention, see Step 3); need to correctly attribute the pro-tempore period (~May 15–22, 2026) — treat any communication in that narrow window as Powell's (he was still chair pro tempore), not Warsh's.

### Step 2 — Market indicator collection
**What:** Pull daily DXY, T10Y2Y, DGS1, IWF, IWN, and DGS3MO for the full window (with a small buffer before Feb 2018 and after today).
**Why:** Needed both for the event-study table (Table 2) and the regression (Table 3); pulling once up front as a clean daily panel is simpler than re-fetching per event.
**How:** `yfinance` for `DX-Y.NYB`, `IWF`, `IWN`; FRED API (`fredapi` + free key) for `T10Y2Y`, `DGS1`, `DGS3MO`. Compute daily returns/changes; align to a shared trading-calendar index (forward-fill or drop on holiday mismatches between FX and Treasury conventions).
**Output:** A local daily panel (gitignored), functions to compute "N-day change ending on date X" for any indicator.
**Watch-outs:** DX-Y.NYB via `yfinance` is occasionally flaky — have a fallback (Stooq) ready; FX markets trade on U.S. holidays when Treasuries don't — need explicit handling, not silent NaNs.

### Step 3 — Tone scoring (3 methods, per Section 3A)
**What:**
1. **Word list / phrase lexicon**: build our own handcrafted lexicon of phrases tagged by topic (Interest Rate, Economy, Job Market, general Sentiment) and sentiment (+1/0/−1); compute per-topic document scores via the sign-aggregation formula from "Parsing the Fed" (Section 3A).
2. **Factor similarity**: FinBERT sentence embeddings, cosine similarity to the two anchor sentences "Inflation will rise" and "Interest rates will rise" → `inf_score` and `rate_score` per document.
3. **FinBERT sentiment**: P(positive) per sentence from ProsusAI/finbert, averaged over the document (baseline); 3-segment scoring as a stretch enhancement if time allows.
**Why these specific implementations, not our own inventions:** directly reproduces "Parsing the Fed"'s pipeline (Section 3A), which is what makes a genuine, formula-level comparison-to-readings section possible instead of a vague "we also did something with FinBERT."
**Output:** Per-document scores for all 3 methods (5 numeric scores total: interest-rate/economy/job-market/sentiment topic scores + inf_score + rate_score + FinBERT sentiment), feeding Figure 1 (time series by doc type, Warsh start marked) and Tables 2/3.
**Watch-outs:** Long documents (minutes can be very long) need chunking before FinBERT (token limits ~512, so segment/chunk and re-average); our word-list lexicon is our own construction (theirs wasn't published in full) — expect to iterate on it after seeing how it scores a few known hawkish/dovish statements as a sanity check, before trusting it on the full corpus.

### Step 4 — Market-reaction validation
**What:** For every release, compute the 1-day change (both event-window versions from Section 3's decisions) in the 4 indicators; regress each indicator's change on that method's score(s) jointly, controlling for ΔDGS3MO — primary regression on statements only, extended version on the full pooled multi-type sample.
**Why controlling for ΔDGS3MO specifically:** the 3-month bill moves mechanically with the *rate decision itself* (it's short-duration, closely tracks the current/near-term fed funds rate); including it as a control isolates the incremental effect of *how the statement is worded*, independent of *what was decided* — exactly the causal question the assignment is asking us to isolate, and the cheap-implementation analog of Doh/Song/Yang's expected-vs-surprise decomposition (Section 3A).
**How:** `statsmodels` OLS. Per method: word-list regression includes all topic scores jointly; factor-similarity regression includes `inf_score` + `rate_score` jointly; FinBERT regression includes the sentiment score (or 3 segment scores if we do the stretch version) — each of these three regressions run separately per indicator, each with the ΔDGS3MO control added. That's 4 indicators × 3 methods = 12 regression models (statements-only), doubled if we also run the pooled multi-type extension.
**Output:** Table 3 (coefficients, significance, R²) directly; a companion table placing our R² next to "Parsing the Fed"'s benchmark R² by method × indicator (Section 3A) for the comparison-to-readings section; the fitted model we'll reuse in Step 5 to translate "expected tone" into "expected market move."
**Watch-outs:** Small-sample caution for the statements-only regression if we further split by era; document-type pooling (the extension) needs type dummies or separate-by-type reporting since statements/minutes/speeches have very different market attention.

### Step 5 — Forecast for Sept 15–16, 2026
**What:** Produce the four required forecast components.
**Why this approach:**
- *Rate decision probabilities*: build a simple historical mapping from tone-score level/trend into subsequent decisions (e.g., ordered logit of "next meeting's decision" on the latest tone score and its recent trend), applied to the July 2026 statement + any pre-meeting Sept communications (blackout period speeches don't exist, but pre-blackout Warsh speeches/testimony do) — then cross-check against public market-implied probabilities (CME FedWatch, fed funds futures) as an external sanity check, not as the source of the number.
- *Statement tone probability*: momentum in the tone series (is it trending more hawkish across Warsh's 2 statements + interim speeches?) plus base rate of tone reversals in the historical Powell series.
- *Market reaction probabilities/magnitudes*: plug the expected tone score (or a small range of scenarios) into the Step 4 regression coefficients to get expected sign and size per indicator, and use residual variance to state a probability of "rises."
- *Recommendation*: one concrete position (e.g., a rates/FX/equity-factor tilt) that follows from the above, with an explicit, checkable condition that would falsify the thesis.
**Output:** Forecast section of the report, in the exact format the rubric specifies.
**Watch-outs:** With only 2 Warsh data points, the historical-mapping model is really trained on Powell-era dynamics and *applied* to Warsh — that's fine and unavoidable, but the report needs to say so explicitly rather than implying a Warsh-specific model.

### Step 6 — Report & repo finalization
**What:** Assemble the PDF report (Tables 1–3, Figure 1, comparison-to-readings discussion, forecast) and finalize the GitHub repo (clean notebook run top-to-bottom, `AI_USE.md` filled in from our actual collaboration log, `README.md`).
**Why AI_USE.md is written from a running log, not reconstructed after the fact:** more accurate, and avoids the failure mode of forgetting/misrepresenting how AI was used, which is exactly what that document exists to prevent.
**Output:** Both deliverables, ready to submit.
**Watch-outs:** Reconfirm "no data files" right before the final commit — easy to accidentally `git add` a cached CSV.

---

## 6. Risks & pitfalls (running list)

- **Time.** 3 days for this scope is tight. We should treat Step 1 (data collection) as the place most likely to blow the budget, and be willing to cut speech-archive breadth (not statements/minutes — those are non-negotiable and small) if it's eating time.
- **Word-list lexicon quality.** Since our phrase lexicon is our own construction (not published in the readings), it needs a sanity-check pass against a few statements with obviously-known tone (e.g., March 2020 emergency cuts = dovish, 2022 hiking cycle statements = hawkish) before we trust it across the full corpus.
- **FinBERT sign ambiguity.** Generic financial sentiment ≠ hawkish/dovish; must validate empirically, not assume.
- **Warsh sample size.** Everywhere we touch Warsh-only data (Table 2, forecast), we must be explicit that N is tiny — both in the code (no false-precision) and in the prose.
- **Release-time data quality.** Speech pages often don't state an exact time; we need a documented, consistent fallback rule rather than ad hoc guessing per document.
- **Fed site structural drift over 8.5 years.** Scraper needs to be tested against a few dates from each era (2018, 2020, 2022, 2024, 2026), not just the most recent format.

---

## 7. How we'll work together

- We go through Sections 5's steps **one at a time**, in order. I won't start Step *n+1* until we've agreed Step *n*'s output is good.
- At the start of each step I'll restate what we're about to do and any open decision inside it before writing code.
- This file gets updated as decisions get made or scope changes — treat Section 3 (decisions log) as append-only history, not something we silently rewrite.
- I'll keep a running note of anything AI-assisted for `AI_USE.md` as we go, rather than reconstructing it at the end.

**Immediate next actions (before Step 0 starts):** confirm repo is empty/public (Section 4 item 2), get the FRED key, confirm time budget, confirm local Python setup — then we clone the repo and start Step 0.

---

## 8. Execution log (v3) — pipeline complete

All open items from Section 4 were resolved and the full pipeline (Steps 0–6) was executed in one continuous session. This section records what actually happened, deviations from the plan, and the real findings — kept separate from Sections 1–7 (the pre-execution plan) so both remain legible as a record of "what we intended" vs. "what we did."

**Environment:** Python 3.13 venv (not 3.14 — confirmed via `pip index versions torch` that PyTorch has no 3.14 wheel yet, so 3.13 was used to avoid a dead end). Benchmarked CPU vs. Apple Silicon MPS for FinBERT inference before committing: MPS was *slower* (0.21s vs 0.07s per batch of 32) for this model/batch size, so CPU was used — a real finding worth keeping in mind for future small-model NLP work, not an assumption.

**Data collected (Table 1 final):** 311 documents total — 304 Powell, 7 Warsh (2 statements, 2 minutes, 2 press conferences, 1 speech). Zero extraction failures across the whole corpus. Exact FOMC meeting dates were pulled directly from federalreserve.gov's historical/calendar pages (not estimated), covering Jan 2018 – Jul 2026. Speeches/testimony were correctly filtered to actual chair-tenure windows (a Powell speech after 2026-05-15 is excluded even though he remains a Governor and kept speaking).

**Tone scoring:** all 3 methods implemented per Section 3A's exact formulas. The word-list lexicon (`src/lexicon.py`, our own construction) passed its sanity check cleanly: March 2020 emergency cuts scored fully dovish (-1.0) on the interest-rate topic, June/Sept 2022 hiking-cycle statements scored fully hawkish (+1.0).

**Real, substantive finding used throughout the forecast:** classifying every statement's decision directly from its text (`src/rate_decisions.py`, searching for "raise/lower/maintain the target range") shows Powell's Fed cutting steadily from mid-2025 through April 2026, then Warsh **held** at his first meeting (June 2026) and **hiked** at his second (July 2026) — a hawkish pivot exactly at the leadership transition, independently corroborated by both the word-list and FinBERT tone scores on those same statements.

**Table 3 finding worth flagging explicitly:** the DGS3MO control's coefficient is large (≈0.8–0.9) and highly significant (p<0.0001) in every 1-year-Treasury regression, and nearly identical R² (~30%) shows up across all four tone methods for that indicator — this is the 3-month bill mechanically co-moving with the 1-year yield on the same days, not tone doing the explanatory work. Net of that control, most individual tone coefficients are *not* significant at conventional levels (n=73 statements) — a modest, honest result consistent with the readings' own effect sizes, not a pipeline bug.

**Forecast, with external validation:** a web search for real market pricing (CME FedWatch, Kalshi, Polymarket) found the Sept 2026 meeting genuinely priced as a "coin flip" (~48-66% hike probability) as of early September 2026, driven by the same catalyst (Warsh's Aug 28 Jackson Hole speech) our text-only model picked up independently — a strong, unplanned validation of the whole approach. Our raw ordinal-logit model output (72.7% hike) was more confident than the market; we explicitly blended the two into a final stated forecast (P(cut)≈5%, P(hold)≈35%, P(hike)≈60%) rather than reporting either alone. Also surfaced: a ceiling effect in the naive tone-momentum calculation (July's word-list score was already at the metric's maximum, mechanically capping "more hawkish" probability) and a direction disagreement between word-list and FinBERT sentiment scores from June→July — both reported honestly rather than resolved away.

**Deliverables produced:**
- `notebooks/analysis.ipynb` — executed top-to-bottom, 20 cells, zero errors, all outputs saved.
- `report/FOMC_Communications_Report.pdf` — the standalone Brightspace report (Table 1, Figure 1, Table 2, Table 3 split by method, comparison-to-readings, forecast+recommendation), built via `src/generate_report.py` (HTML → weasyprint). Kept **out of the GitHub repo** (gitignored) since it's the separate Brightspace deliverable, not a code/notebook artifact — delivered to the user directly.
- GitHub repo pushed twice: scaffold+scraping commit, then the full tone-scoring/regression/forecast/notebook commit.
- `AI_USE.md` rewritten with a specific, honest account of what was AI-generated vs. jointly decided (see that file).

**Known limitations carried into the report itself** (not hidden): Warsh-era N is tiny by construction; the word-list lexicon is our own construction, not a published one; we use daily close-to-close changes, not intraday tick data (matching "Parsing the Fed"'s own simplification); the Doh et al. alternative-statement method is structurally inapplicable post-~2021 due to the 5-year declassification lag.

---

## 9. Post-delivery bug fix: minutes were assigned the wrong release date

Found by the user asking a clarifying question about the regression design ("what if two documents release at the same time?"), which led to checking whether our event-study windows actually reflect each document's *real* release date. They don't, for one document type. This section is the plan for the fix, written before touching any code, specifically to trace the full blast radius before acting — not just patch the symptom.

### The bug, precisely

`scrape_fomc_core.py`'s `scrape_minutes()` stores `"date": date`, where `date` is the **meeting date** (e.g. `20260729`) — because that's what's embedded in the Fed's minutes URL (`fomcminutes20260729.htm`). But FOMC minutes are not published on the meeting date; they're published **about three weeks later**. `event_study.py` reads that `date` field directly as "when was this released" and computes the one-day market window around it — so every minutes document's "market reaction" is actually measuring the market's reaction to *that day's statement and press conference*, not the minutes (which weren't even public yet).

### Verified against the live site before writing any fix (not assumed)

Re-checked three minutes pages spanning the full window, specifically looking for a reliable field holding the true publication date:

| Meeting date | `lastUpdate` div on the minutes page | Gap |
|---|---|---|
| 2018-01-30/31 | February 21, 2018 | 21 days |
| 2026-06-16/17 | July 08, 2026 | 21 days |
| 2026-07-28/29 | August 19, 2026 | 22 days |

The `lastUpdate` div is consistent, present across the whole 2018–2026 window, and matches the well-known ~3-week convention. **Explicitly ruled out a trap**: the minutes' own body text contains the phrase "for release at 2:00 p." — but that's describing the policy directive's effective time (content *within* the minutes), not the minutes document's own publication date. Confirmed this isn't the field to parse.

### Addendum, written during execution: the plan above was itself revised before shipping

The 3-example spot-check above looked solid enough to proceed on `lastUpdate` alone. Before actually writing the extraction code, a wider check was run across all 69 minutes documents (once the field was being scraped programmatically rather than checked by hand one at a time) — and one came back with a 65-day gap: the Sept 21–22, 2021 meeting's `lastUpdate` read "November 26, 2021." An independent web search confirmed the *true* release date was October 13, 2021 — `lastUpdate` was off by 44 days. It turns out `lastUpdate` reflects whenever the page was last technically touched (a later, unrelated edit), not necessarily the original publication date.

**Revised approach, used in the actual implementation:** compute the release date directly from the Fed's own stated, consistent policy — 21 calendar days after the meeting's second day — verified against 5 independently-confirmed real dates (adding Sept 2021 and Dec 2018 to the 3 above), including a December/holiday-season meeting, all matching exactly. `lastUpdate` is kept only as a diagnostic cross-check (flagged if it disagrees with the computed date by more than 3 days), not the source of truth. This is a stronger, more defensible fix than the one originally planned in this section, and it was only strengthened because we happened to check all 69 cases instead of stopping at 3 examples that agreed. See [Step 17](../docs/steps/17-post-delivery-bug-fix.md) for the full account.

### The fix, designed for minimum blast radius

Add a new field, populated only by `scrape_minutes()`, holding the true release date parsed from `lastUpdate`. Everything else about how a "document" is identified (the `date` field used as the join key across every table) **stays exactly as it is** — we are not renaming or repurposing that key, only adding a second, purpose-specific date used exclusively for picking the correct market-data window. `build_corpus.py` defaults this new field to the existing `date` for every document type where the two are already the same (statements, press conferences, speeches, testimony — none of which have this problem), so only `scrape_fomc_core.py` and two downstream files need code changes.

### Full blast-radius trace, before doing anything

**Code files that need to change (4):**
1. `src/scrape_fomc_core.py` — `scrape_minutes()` gains a new `actual_release_date` field, parsed from `lastUpdate`.
2. `src/build_corpus.py` — parses that field into a real `release_date_dt` column (defaulting to the existing `date_dt` when the field is absent), and computes `release_hour_et` / `released_before_close` from *that* date instead of the meeting date. Minutes' time-of-day convention (2:00 p.m. ET) is unchanged — only which *date* it applies to changes.
3. `src/event_study.py` — swaps `date_dt` for `release_date_dt` as the anchor for window lookups. One variable change; identical logic otherwise.
4. That's it for code. No changes to `lexicon.py`, `tone_word_list.py`, `tone_finbert.py`, `rate_decisions.py`, `make_figure1.py`, `fetch_market_data.py`, `scrape_speeches_testimony.py`, `forecast.py`, or `run_regressions.py` themselves — their *outputs* change where downstream of the fix, but their code doesn't need to.

**Data artifacts that must be regenerated (all fast — no new network calls, everything re-parses already-cached HTML/JSON):**
`fomc_core_documents.json` → `corpus.parquet` → `event_changes.parquet` → `master_dataset.parquet` → `table3_regressions.csv` → `table2_warsh_era.csv` → `forecast_market_reaction.csv` (re-run to *confirm* unchanged, see below).

**Data artifacts that do NOT need to be touched, and why (this is the important part to get right):**
- `scores_word_list.parquet`, `scores_finbert.parquet` — tone scores are computed from document *text*, never from date. The `date` join key they use is unchanged. **The ~13-minute FinBERT run does not need to be redone.**
- `market_panel.csv` — the raw market data itself is correct and untouched; we're only fixing *which day* of it we look up for minutes.
- `rate_decisions.csv` — built from statement text only; minutes never enter it.
- `figure1_tone_over_time.png` — built from tone scores only, no market data involved at all.

**What actually changes in the numbers, and what doesn't:**
- Table 2's minutes rows — **will change** (correctly, to reflect the real ~3-week-later market window).
- Table 3's `pooled_core_docs` regression (statements+minutes+presconf) — **will change**, since ~1/3 of its 207 rows had the wrong window.
- Table 3's `statements_only` regression (the report's primary, headline result) — **mathematically cannot change**: it never included minutes rows in the first place. Re-running it should reproduce identical numbers; if it doesn't, that itself would be a signal something else broke.
- The forecast (`forecast.py`) — reads only statement-level tone and the `statements_only` Table 3 row for its market-reaction scenario, so its numbers **should not change**. Re-run it anyway to *confirm* that, not assume it.
- The DGS3MO-confound finding, the "Parsing the Fed" comparison, the whole forecast section — all live in the unaffected statements-only world and stand as reported.

**Deliverables that need regenerating as a consequence:**
- `notebooks/analysis.ipynb` — re-executed top to bottom (it displays both the statements-only *and* pooled Table 3, so the pooled section's numbers will visibly update).
- `report/FOMC_Communications_Report.pdf` — regenerated (its Table 2 will change; its Table 3 only ever showed statements-only, so that section is unaffected in value but gets rebuilt for consistency).

**Documentation that needs an honest correction, not a silent rewrite:**
- `AI_USE.md` — a new, specific entry: this was a mistake in the original implementation, caught by the user's question, not by us.
- `README.md` — the Step 10/11 summary paragraphs need to reflect the corrected behavior.
- `docs/steps/04-scraping-fomc-core-documents.md` and `docs/steps/10-event-study.md` — both describe the original (buggy) design as if it were simply correct; each gets a dated correction note, not a quiet edit that erases the fact a bug existed.
- `docs/steps/12-figures-tables-and-decisions.md` — Table 2 is discussed there directly; needs the corrected framing.
- A new `docs/steps/17-post-delivery-bug-fix.md`, added to `docs/STORY.md`'s index, telling this correction as its own honest chapter — because it happened after "shipping," not before, and the story should say so rather than pretend it was caught in Step 10 originally.

### Sequencing

1. Code changes (4 files above).
2. Regenerate the data artifacts in dependency order, checking at each step that the "should not change" numbers really don't.
3. Re-execute the notebook; verify zero errors again.
4. Regenerate the PDF; spot-check the corrected Table 2 visually.
5. Update `AI_USE.md`, `README.md`, the affected `docs/steps/*.md` files, add the new Step 17 doc, update `STORY.md`.
6. New git commit (not amended — the original commits stay as an honest record of what was actually shipped when), push.
7. Re-deliver the corrected PDF to the user.
