# Step 8: Tone Scoring — Word List (Method 2)

This is the first of the three tone-scoring methods identified in [Step 2](02-reading-the-research-papers.md), and the one requiring the most original construction on our part (the readings only show illustrative examples of their lexicon, not a published list — ours had to be built from scratch).

## `src/text_utils.py`

**What it does:** one function, `split_sentences()`, that breaks a document's text into individual sentences using NLTK's `punkt` tokenizer (downloaded once, checked for first via `nltk.data.find` so re-runs don't re-download it). We tested it against a deliberately tricky sentence first — `"The U.S. economy grew 3.5 percent. Inflation remained low, at 2.1 percent, per Mr. Powell."` — to confirm it correctly handles abbreviations like "U.S." and "Mr." without splitting on their periods, since a naive `text.split(".")` would have shredded the corpus into garbage fragments right at the word "U.S."

**Why it was necessary:** all three tone-scoring methods operate at the sentence level (the word-list method looks for phrases within a sentence; both FinBERT methods score sentence-by-sentence and aggregate). Getting sentence boundaries right is the foundation everything else in this step and the next is built on.

## `src/lexicon.py`

**What it does:** the actual hand-built phrase lexicon — roughly 100 phrases, each tagged with a topic (`interest_rate`, `economy`, `job_market`, `sentiment`) and a direction (+1 hawkish, -1 dovish). Examples: `"raise the target range"` (interest_rate, +1), `"inflation has eased"` (sentiment, -1), `"labor market remains tight"` (job_market, +1), `"economic activity has slowed"` (economy, -1). Matching is bag-of-words within a sentence — a phrase counts as present if *all* its words appear anywhere in the sentence, not necessarily adjacent — which directly follows "Parsing the Fed"'s own stated approach ("words in a phrase need not be consecutive").

**Why it was necessary, specifically:** the assignment's own worked example — "higher inflation" is hawkish, "inflation has eased" is dovish — proves that a simple word-frequency count (counting how often "inflation" appears) carries *no* directional signal on its own. The direction lives entirely in the modifier around it. A lexicon of single words would have scored both of those phrases identically. Building phrases, not words, was not optional.

## `src/tone_word_list.py`

**What it does:** implements the exact scoring formula from "Parsing the Fed":

$$x_k(t) = \frac{1}{n_k}\sum_i \text{sign}\left(\sum_p L(p) \cdot S(p) \cdot \mathbb{1}_k(i)\right)$$

For each topic $k$, look at every sentence $i$ in the document; for every lexicon phrase $p$ of that topic present in that sentence, add up phrase-length-weighted sentiment; take the *sign* of that sum for the sentence (so one strongly-worded phrase doesn't drown out three weakly-worded opposite ones — the reading's own formula, reused as-is); average that sign across every sentence that mentioned the topic at all ($n_k$ of them). The result is a score between -1 (fully dovish) and +1 (fully hawkish) per topic, per document.

**Why this specific formula, rather than a simpler count-based average:** it was the reading's own method, and reproducing it exactly (rather than inventing a superficially similar but different formula) is what makes the later "how do our results compare to the readings" section a real comparison instead of an approximate one.

## The sanity check — and why it mattered

Before trusting this lexicon on all 311 documents, we ran it against a handful of statements with *known* real-world tone: the March 2020 emergency COVID rate cuts (should be maximally dovish) and the June/September 2022 statements from the height of the hiking cycle (should be maximally hawkish). Because this lexicon was our own construction — not a published, pre-validated one — skipping this check would have meant trusting an unverified instrument for the rest of the project.

**Result of the sanity check:**

| Date | Real-world context | `wl_interest_rate` score |
|---|---|---|
| 2020-03-03 | Emergency 50bp cut | **-1.0** (fully dovish) |
| 2020-03-15 | Emergency cut to zero | **-1.0** (fully dovish) |
| 2022-06-15 | 75bp hike, peak hiking cycle | **+1.0** (fully hawkish) |
| 2022-09-21 | 75bp hike, peak hiking cycle | **+1.0** (fully hawkish) |

Four for four, correctly signed at the extremes. This is what let us trust the lexicon on the full corpus with confidence rather than hope.

## Result on the full corpus

Running the scorer across all 311 documents produced four topic scores per document (`wl_interest_rate`, `wl_economy`, `wl_job_market`, `wl_sentiment`), saved to `data/processed/scores_word_list.parquet`. Summary statistics showed real variation (not everything collapsing to zero or saturating at ±1), and — most tellingly — both of Warsh's 2026 statements scored **+1.0 on `wl_sentiment`** (fully hawkish inflation language) and July's scored **+1.0 on `wl_interest_rate`** as well, foreshadowing the hawkish-pivot finding that became central to the whole forecast (see [Step 12](12-figures-tables-and-decisions.md)).

**Next:** [Step 9 — Tone Scoring: FinBERT](09-tone-scoring-finbert.md).
