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
