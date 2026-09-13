# AI Use Disclosure

This project was built collaboratively with Claude (Anthropic), used as a coding and research assistant throughout. This log is kept running as we work, rather than reconstructed after the fact.

## How AI was used

- **Planning:** Claude read the assignment sheet and the three assigned readings (Doh, Kim & Yang 2021; Doh, Song & Yang 2020/2023; the "Parsing the Fed" presentation) in full, and drafted a step-by-step methodology plan (`PLAN.md`), which was reviewed and iterated on collaboratively rather than accepted as-is.
- **Research:** Claude used web search to establish real-world facts needed to scope the project (Kevin Warsh's swearing-in date, FOMC meeting calendar for 2026), since these postdate the model's training data.
- **Implementation:** Claude wrote the scraping, tone-scoring, and regression code under direction, following the methodology in `PLAN.md`.
- **Analysis and writing:** [to be filled in as we go — e.g., interpretation of regression results, drafting of report sections]

## What was not AI-generated

- All methodology decisions (e.g., which tone-scoring methods to use, how to handle the event-study window, how to structure the forecast) were made jointly, with rationale recorded in `PLAN.md`, not delegated wholesale to the AI.
- [Update this section with specifics as the project progresses.]

## Tools

- Claude (Anthropic), via Claude Code
- FinBERT (ProsusAI/finbert, Hugging Face) — used as one of the three tone-scoring methods, per the assignment's own suggestion
