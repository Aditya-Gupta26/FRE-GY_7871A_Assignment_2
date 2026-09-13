# Step 2: Reading the Research Papers

**No code in this step** — but this is where the project's actual methodology got locked in, so it's the most consequential non-coding step in the whole story.

## What happened

You uploaded three PDFs: Doh, Kim & Yang (2021) "How You Say It Matters," Doh, Song & Yang (2020/2023) "Deciphering Federal Reserve Communication," and a presentation deck called "Parsing the Fed." Each was read in full (all pages, not summaries) because the assignment explicitly asks us to "build on" and "compare against" these readings — which is impossible to do honestly without knowing what's actually in them.

## The discovery that changed the plan

**"Parsing the Fed" turned out not to be an academic paper at all — it reads as a prior student project, and it is structurally almost identical to this assignment.** It uses the exact same four market indicators (DXY, 10s2s spread, 1-year Treasury, Growth-minus-Value) and compares the exact same three tone-scoring methods the assignment nudges us toward (a word list, FinBERT sentiment, and a third "factor similarity" method). That's not a coincidence — this assignment is a guided replication of that prior work, extended in scope. Once we saw that, the plan changed from "invent three reasonable tone-scoring methods" to "reproduce these three specific methods, with their exact formulas, then extend the time window and add what they didn't do (Powell-vs-Warsh comparison, a forecast)."

Concretely, we extracted:

- **Method 1 (Factor similarity):** embed sentences with FinBERT, measure cosine similarity to two anchor sentences — literally "Inflation will rise" and "Interest rates will rise" — and average per document. Two scores per document: `inf_score`, `rate_score`.
- **Method 2 (Word list):** a hand-built phrase lexicon tagged by topic (Interest Rate, Economy, Job Market, Sentiment) and hawkish/dovish sign, matched bag-of-words within a sentence (words in a phrase need not be adjacent), aggregated via a specific sign-based formula.
- **Method 3 (FinBERT sentiment):** P(positive) per sentence from FinBERT's classification head, averaged over the document, with a 3-segment (thirds of the document) refinement shown to improve fit.
- Their own reported R² benchmarks by method and indicator, which we could later place our own results next to.

From the two Doh et al. papers, we learned their (more sophisticated) approach: compare each official statement's embedding against the Fed's own internally-drafted "alternative statements" (a deliberately dovish version, a consensus version, a deliberately hawkish version), which Fed staff prepare before every meeting. **Critically, these alternative statements are only released to the public after a 5-year lag.** That single fact turned out to matter enormously: it meant that method is *structurally impossible* to apply to the Warsh era, or to anything from roughly 2021 onward — not a limitation of our effort, but a real constraint anyone doing this analysis today would hit. We decided not to attempt a partial replication of it as a fourth method, and instead to state this limitation plainly in the report rather than pretend it away.

We also learned their surprise-decomposition approach uses **intraday bond-futures tick data** in narrow (10–90 minute) windows around announcements — data we don't have access to. "Parsing the Fed" hit the same wall and fell back to daily close-to-close changes, which is exactly what our own data sources (Yahoo Finance, FRED) support. Knowing this in advance meant we could state it as a shared, explicit simplification rather than discover it partway through and scramble.

## Why this step mattered so much

Without it, the "comparison to the readings" section of the final report would have been generic ("we also used FinBERT, like some other researchers have"). With it, we could write a comparison with actual formulas, actual benchmark numbers, and an honest account of exactly two places where we structurally cannot match the more sophisticated papers — which is a stronger, more credible report than one that quietly ignores the mismatch.

## Result

`PLAN.md` was substantially rewritten (v2): a new Section 3A was added laying out exactly what we were borrowing from each reading, several earlier "we'll figure this out" placeholders were replaced with concrete formulas, and the decisions table was updated (e.g., "word-list scoring is phrase-based, topic-tagged, sign-aggregated per the exact formula" replaced the vaguer v1 language of "some kind of bigram approach").

**Next:** [Step 3 — Environment & Repo Setup](03-environment-and-repo-setup.md), where the actual coding starts.
