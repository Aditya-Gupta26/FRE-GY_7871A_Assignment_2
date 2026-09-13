# AI Use Disclosure

This project was built collaboratively with Claude (Anthropic, Claude Code), used as a research and coding assistant throughout. This log reflects the actual session, not a reconstruction.

## How AI was used

- **Planning:** Claude read the assignment sheet and the three assigned readings (Doh, Kim & Yang 2021; Doh, Song & Yang 2020/2023; the "Parsing the Fed" presentation) in full, and drafted a step-by-step methodology plan (`PLAN.md`). The plan was reviewed and revised collaboratively — e.g. the decision to implement 3 tone-scoring methods instead of the required 2, the choice of a phrase-based lexicon over unigram word counts, and the two-window event-study design were all discussed and justified, not accepted from a first draft.
- **Research:** Claude used web search to establish real-world facts that postdate its training data and that the whole project depends on: Kevin Warsh's swearing-in date (2026-05-22), the 2026 FOMC meeting calendar, and — for the forecast section — actual market-implied probabilities (CME FedWatch, Kalshi, Polymarket) for the September 2026 meeting, used only as an external cross-check on our own model, not as the source of our numbers.
- **Implementation:** Claude wrote all scraping (`src/scrape_fomc_core.py`, `src/scrape_speeches_testimony.py`), tone-scoring (`src/lexicon.py`, `src/tone_word_list.py`, `src/tone_finbert.py`), event-study (`src/event_study.py`), regression (`src/run_regressions.py`), rate-decision classification (`src/rate_decisions.py`), and forecasting (`src/forecast.py`) code, under direction and following the methodology recorded in `PLAN.md`.
- **Debugging:** Claude benchmarked CPU vs. Apple Silicon MPS for FinBERT inference before committing to a device (MPS was actually slower for this model/batch size — a real finding, not an assumption), and fixed a handful of implementation bugs found while running the pipeline (a dtype mismatch in the forecast merge, an operator-precedence bug in an early draft of the market-reaction forecast, a missing intercept term in the regression output needed for the forecast).
- **Analysis and writing:** Claude ran the full pipeline, surfaced and interpreted results (e.g., flagging that the 1-year-Treasury regression's R² was being driven almost entirely by the 3-month-bill control rather than tone — the exact confound the assignment's control is designed to catch; flagging a ceiling effect in the tone-momentum forecast; noting the disagreement in direction between the word-list and FinBERT sentiment scores from June to July 2026), and drafted the report and notebook narrative around those findings.

## What was not AI-generated / was a joint decision

- All methodology decisions — which tone-scoring methods to use, how to define the event-study windows, how to structure the regressions (per-method joint regressors vs. univariate), which corpus to use as primary vs. extension, and how to blend the model's rate-decision forecast with the real-world market cross-check into a final stated probability — were made jointly and are recorded with rationale in `PLAN.md`.
- The hand-built phrase lexicon (`src/lexicon.py`) reflects domain judgment about what counts as hawkish/dovish monetary-policy language; it was sanity-checked against statements of known tone (March 2020 emergency cuts scored fully dovish, June/Sept 2022 hiking-cycle statements scored fully hawkish) before being trusted on the full corpus.
- The final recommendation and its stated falsification condition are a judgment call, explicitly weighing the model's own (likely overconfident) output against real market pricing, not a number generated and reported uncritically.

## Tools

- Claude (Anthropic), via Claude Code
- FinBERT (`ProsusAI/finbert`, Hugging Face) — used for two of the three tone-scoring methods, per the assignment's own suggestion
- Data sources: federalreserve.gov (documents), Yahoo Finance and FRED (market data) — see `README.md`
