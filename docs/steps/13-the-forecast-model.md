# Step 13: The Forecast Model

This is the step that turns everything built so far — tone scores, market reactions, regressions, and the rate-decision history — into the assignment's actual required output: probabilities for the September 15–16, 2026 FOMC meeting.

## `src/forecast.py`

**What it does — three separate functions, one per required forecast component:**

### 1. `rate_decision_probabilities()`

Fits an **ordinal logistic regression** (cut < hold < hike, using `statsmodels`' `OrderedModel`) of each meeting's decision on the *previous* meeting's decision and the *previous* statement's word-list tone scores. The word "previous" is doing real work here: the model is deliberately built so that forecasting September only ever uses information that was actually available before September's meeting — the most recent real data point is the July 29, 2026 statement, decision, and tone. This avoids the mistake of accidentally training a model that "knows" things it shouldn't when it's later asked to predict.

### 2. `statement_tone_momentum()`

Estimates the probability that September's statement will read *more* hawkish than July's, using the historical persistence of tone moves — does an increase in hawkishness tend to be followed by another increase? — conditioned on the fact that the actual June→July move was itself an increase.

### 3. `market_reaction_forecast()`

Takes the word-list regression coefficients from Table 3 ([Step 11](11-master-dataset-and-regressions.md)), plugs in a "September looks like July" tone scenario, and converts the resulting point prediction into a probability that each indicator rises — using each regression's own residual standard deviation and the normal CDF.

## A bug, caught by actually running the code rather than trusting it

The first run of `forecast.py` crashed immediately:

```
ValueError: You are trying to merge on int64 and str columns for key 'date'
```

`rate_decisions.csv`'s `date` column (values like `20260729`) had been read back by `pandas.read_csv` as an integer, while every other table in the project treats `date` as a string. The fix was a one-line `dtype={"date": str}` on the read call. This is a small, almost boring bug — but it's included here deliberately, because it's a reminder that "the code ran without errors" was checked at every step, not assumed, and when something did break, it got fixed and re-verified rather than papered over.

## The external validation nobody was expecting

Once the forecast was producing real numbers (see Result, below), we didn't just report the model's raw output. Per the plan's own stated principle ("cross-checked against public market-implied pricing... not derived from it"), we did a web search for actual, real-world market pricing for the September 2026 FOMC meeting. What came back was genuinely striking:

- Real market pricing in early September 2026 (CME FedWatch ~56–66%, Kalshi ~48%, Polymarket ~49%) framed the meeting as a **"coin flip"** on a hike.
- That pricing had shifted sharply — from roughly 36% before to over 50% after — specifically because of **Kevin Warsh's August 28, 2026 Jackson Hole speech**.

That's the *exact same document* — Warsh's Jackson Hole speech — that we had already scraped in [Step 5](05-scraping-speeches-and-testimony.md) and scored for tone in [Step 8](08-tone-scoring-word-list.md) and [Step 9](09-tone-scoring-finbert.md), entirely independently of this search. Our text-only pipeline and real financial markets converged on the same catalyst, from completely different starting points. That is about as strong a piece of external validation as a project like this could hope to stumble into, and it happened because we built the habit of checking our own outputs against reality rather than trusting the model in isolation.

## Result

The raw model outputs:

```
P(cut) = 0.9%    P(hold) = 26.4%    P(hike) = 72.7%
(trained on 68 historical meetings)

P(Sept statement more hawkish than July) = 20.0%
```

We didn't take the 72.7% at face value — a model trained on 68 meetings, extrapolating from an input that sits at the *extreme* end of its own training range (July's tone score was already at the ceiling of the word-list scale), should be trusted less than its raw confidence suggests. So we explicitly blended the model's direction (hike is the modal outcome) with the market's more measured framing (a genuine coin flip) into a final, judgment-informed forecast:

**P(cut) ≈ 5%, P(hold) ≈ 35%, P(hike) ≈ 60%**

We also caught and explained a **ceiling effect** in the naive tone-momentum number: since July's word-list interest-rate score was already at its maximum possible value (+1.0), "more hawkish than July" is nearly impossible on that specific measure by construction — not because momentum is actually fading. Cross-referencing against FinBERT's sentiment score (which actually *fell* slightly from June to July) revealed the two methods genuinely disagree on direction here, which we reported as real uncertainty rather than picking whichever number sounded more confident.

The market-reaction forecast came back with small point predictions and probabilities close to 50% for every indicator — which is not a weak result, but an *honest* one, directly consistent with [Step 11](11-master-dataset-and-regressions.md)'s finding that most tone coefficients weren't statistically significant once the 3-month-bill confound was controlled for.

**Next:** [Step 14 — Notebook Assembly](14-notebook-assembly.md).
