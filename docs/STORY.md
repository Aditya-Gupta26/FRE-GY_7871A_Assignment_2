# The Build Story: How This Project Came Together

This is the central index for a chronological, step-by-step account of how this entire assignment — the FOMC tone-analysis pipeline, the notebook, and the PDF report — was built, from the first question ("what is the Fed?") to the final commit. Each linked file covers one phase: what we did, every code file involved in that phase (what it does, why it was necessary), and the actual results it produced.

Read them in order for the full story, or jump to the phase you care about.

## Why this document exists

You asked for something you could have done yourself, but chose to hand off — and now you want to actually understand what happened, file by file, so the work is legible rather than a black box. This index and the 17 files it links to are that account, written after the fact but as faithfully as possible to the real order things happened in (including the dead ends, bugs found, and mid-course corrections — not a cleaned-up version that pretends everything worked on the first try). That includes a real bug found *after* the original delivery ([Step 17](steps/17-post-delivery-bug-fix.md)) — left in the story rather than quietly folded into earlier steps as if it were always known.

## The chronological story

| # | Phase | What happened | Code files |
|---|---|---|---|
| 1 | [Understanding the Assignment](steps/01-understanding-the-assignment.md) | Read the assignment PDF, figured out the Kevin Warsh/Fed-chair scenario was real (not hypothetical) and postdated training data, verified the actual 2026 timeline via web search, built the first draft plan | — |
| 2 | [Reading the Research Papers](steps/02-reading-the-research-papers.md) | Read all three assigned readings in full, discovered "Parsing the Fed" was a near-identical prior project, extracted exact formulas to reuse | — |
| 3 | [Environment & Repo Setup](steps/03-environment-and-repo-setup.md) | Set up the git repo, Python venv (with a real Python-version compatibility catch), `.gitignore`, secrets handling, project scaffold | — |
| 4 | [Scraping FOMC Core Documents](steps/04-scraping-fomc-core-documents.md) | Reverse-engineered federalreserve.gov's URL structure, built the statement/minutes/press-conference scraper | `config.py`, `scrape_utils.py`, `scrape_fomc_core.py` |
| 5 | [Scraping Speeches & Testimony](steps/05-scraping-speeches-and-testimony.md) | Found the speech/testimony archive pattern, filtered to actual chair-tenure dates | `scrape_speeches_testimony.py` |
| 6 | [Collecting Market Data](steps/06-collecting-market-data.md) | Pulled the 4 indicators + control from Yahoo Finance and FRED | `fetch_market_data.py` |
| 7 | [Building the Corpus](steps/07-building-the-corpus.md) | Merged both document scrapes into one dataset with parsed release timestamps | `build_corpus.py` |
| 8 | [Tone Scoring — Word List](steps/08-tone-scoring-word-list.md) | Built the hand-crafted hawkish/dovish phrase lexicon and the sign-aggregation scorer | `text_utils.py`, `lexicon.py`, `tone_word_list.py` |
| 9 | [Tone Scoring — FinBERT](steps/09-tone-scoring-finbert.md) | Loaded FinBERT, benchmarked CPU vs. Apple GPU (counterintuitive result), scored factor similarity + sentiment | `tone_finbert.py` |
| 10 | [Event Study](steps/10-event-study.md) | Computed one-day market changes around every release, two ways | `event_study.py` |
| 11 | [Master Dataset & Regressions](steps/11-master-dataset-and-regressions.md) | Merged everything, ran Table 3's regressions, found (and correctly interpreted) a confound | `build_master_dataset.py`, `run_regressions.py` |
| 12 | [Figures, Tables & Rate Decisions](steps/12-figures-tables-and-decisions.md) | Built Figure 1, Table 2, and a from-scratch rate-decision classifier that surfaced the key finding of the whole project | `make_figure1.py`, `make_table2.py`, `rate_decisions.py` |
| 13 | [The Forecast Model](steps/13-the-forecast-model.md) | Built the ordinal-logit forecast, hit and fixed a bug, cross-checked against real market pricing | `forecast.py` |
| 14 | [Notebook Assembly](steps/14-notebook-assembly.md) | Assembled and executed the deliverable notebook cell by cell | `notebooks/analysis.ipynb` |
| 15 | [PDF Report Generation](steps/15-pdf-report-generation.md) | Built the standalone Brightspace report, fixed two rounds of layout bugs | `generate_report.py` |
| 16 | [Finalizing & Shipping](steps/16-finalizing-and-shipping.md) | Wrote up `AI_USE.md` honestly, closed the loop in `PLAN.md`, committed and pushed three times, delivered the PDF | `AI_USE.md`, `PLAN.md`, `.gitignore` |
| 17 | [Post-Delivery Bug Fix](steps/17-post-delivery-bug-fix.md) | A user question surfaced a real bug (minutes were assigned the meeting date instead of their true ~3-week-later publication date); planned the fix's full blast radius before touching code, fixed it, verified the headline results and forecast were mathematically unchanged, documented it honestly | `scrape_fomc_core.py`, `build_corpus.py`, `event_study.py` |

## The one-paragraph version

We read the assignment and discovered it was set in a real (if very recent) future — Kevin Warsh actually did become Fed Chair in May 2026 — so before writing any code we verified the real timeline via web search rather than guessing. We then read all three assigned papers in full and found that one of them, "Parsing the Fed," was essentially a prior version of this exact assignment, which let us borrow its exact formulas instead of inventing our own. From there it was a straight build: scrape the Fed's site for every statement, minutes set, press-conference transcript, speech, and testimony from 2018–2026 (311 documents, zero failures); pull the four market indicators plus a control from Yahoo/FRED; score every document's tone three ways (a hand-built lexicon, FinBERT embedding similarity, and FinBERT sentiment); compute how markets moved around every release; regress one on the other while controlling for the confound the assignment specifically warns about; and use all of it to forecast the September 2026 meeting — a forecast that, when cross-checked against real market pricing we looked up along the way, turned out to agree on direction with actual traders for the actual reason (a hawkish speech Warsh gave in late August), which was the most convincing piece of validation in the whole project.

## Where everything lives

- **Code:** `src/` (18 files, one per phase above)
- **Notebook:** `notebooks/analysis.ipynb`
- **Report generator:** `src/generate_report.py` → `report/FOMC_Communications_Report.pdf` (not committed — see Step 16)
- **Planning record:** `PLAN.md` (written *before* execution, plus a Section 8 execution log and a Section 9 post-delivery bug-fix plan, both appended *after*, so you can see intention vs. outcome side by side)
- **AI disclosure:** `AI_USE.md`
- **Data:** `data/` — gitignored, regenerated by running the scripts in dependency order (see each step's "how to reproduce")
