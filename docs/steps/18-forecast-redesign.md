# Step 18: Forecast Redesign — Fixing a Model That Wasn't Forecasting Anything

This is the second post-delivery correction (see [Step 17](17-post-delivery-bug-fix.md) for the first, the minutes release-date bug). This one is more conceptual than that one — not a wrong date fed into otherwise-correct code, but a piece of the forecast that couldn't have produced a real forecast no matter what data went into it.

## How it was found: by being asked to explain it, and the explanation not holding up

Walking back through `market_reaction_forecast()` to answer a question about the regression design, the actual mechanism became impossible to defend once stated plainly: the function plugged July's own tone scores into Table 3's statements-only word-list regression — a regression that had been **fit using July's own row** as one of its 73 training observations. Plugging July's tone back in therefore just returns the model's in-sample fitted value for July. The exact framing that nailed it: *"Piece 3 result should then just be July's result as the OLS predicts."* Correct — mathematically, that is all the original code could ever produce, no matter how the rest of the pipeline was built.

A related, smaller problem lived in the same file: `statement_tone_momentum()` was a 2-bucket frequency lookup (did an increase tend to follow an increase?), not a trained model at all, and its output was mechanically distorted — July's `wl_interest_rate` score already sat at the scale's maximum, so "a further increase" looked artificially rare regardless of true momentum.

## Design options discussed and rejected before landing on the final approach

This redesign went through several rounds of proposal-and-pushback before converging — worth recording, since the rejected options are as informative as the final one:

1. **Decision-probability-weighted conditional means.** Compute the historical average tone score conditional on decision type (cut/hold/hike), then weight by Piece 1's own P(cut)/P(hold)/P(hike). Workable, but creates a dependency on an *estimated* quantity (Piece 1's probabilities) where a simpler option turned out not to need one.
2. **A plain AR(1) per topic.** Regress each topic's score on its own lag alone. Risked just pulling every forecast toward the unconditional historical mean — Figure 1 shows tone moving in long regime-like stretches, not smooth mean-reverting noise, so a naive AR(1) would likely have thrown away exactly the signal that matters most (the current hawkish regime).
3. **An intermediate version needing `E[decision_code(September)]`.** Predicting September's tone from *that same meeting's* decision requires knowing (or estimating) September's decision — which isn't known, so this route needed Piece 1's probabilities converted into an expected value and fed back in. Dropped once it was pointed out that using only *lagged* predictors (July's already-known values) sidesteps the need to estimate anything at all.
4. **Retraining Table 3 itself with lagged inputs.** Proposed directly: should Table 3 also predict "this meeting's market reaction" from "last meeting's tone"? Discussed and rejected jointly — that would answer a different, economically dubious question (does stale, already-priced-in information predict today's market move — no reason it should in an efficient market), and would stop matching what the assignment's own Table 3 requires (contemporaneous tone explaining that same release's own reaction). Table 3 was left exactly as originally fit in [Step 11](11-master-dataset-and-regressions.md), never retrained.

## The final design: one shared, lagged predictor set, only the target changes

$$x = [\text{lag\_decision\_code},\ \text{lag\_wl\_interest\_rate},\ \text{lag\_wl\_economy},\ \text{lag\_wl\_job\_market},\ \text{lag\_wl\_sentiment}]$$

— each meeting's own decision and all four word-list topic scores, lagged by exactly one meeting. For September, `x` is simply **July's real, known values** — no estimation needed, since July is the meeting immediately before the one being forecast. Three model types share this `x`, differing only in `y`:

1. **`rate_decision_probabilities()`** — `y` = this meeting's own decision (ordinal logit, unchanged model type, extended to use all four topics instead of two — see the honest note below on why).
2. **`forecast_tone_scores()`** (new) — `y` = this meeting's own topic score, one OLS per topic. This is the actual fix: predicts September's real tone from July's real values, and this specific input combination was never part of any training row (September doesn't exist in the training data), so it's a genuine forecast, not a replay.
3. **`statement_tone_momentum()`** — `y` = binary, was `wl_interest_rate` higher than the previous statement's (logistic regression, replacing the lookup).

`market_reaction_forecast()` is **not retrained**. It now consumes `forecast_tone_scores()`'s real September prediction as the scenario fed into Table 3's already-fitted, unchanged coefficients — the same "plug tone into fitted coefficients" arithmetic as before, just with a legitimate input for the first time.

## An honest note on a mistake made mid-discussion, and caught before it shipped

Partway through, simplifying toward this design, `lag_decision_code` got dropped from the shared predictor set — matching an example written out using only the four tone topics. That was a mistake worth owning specifically: the *original* 3-predictor rate-decision model had already shown `lag_decision_code` was the only statistically significant predictor (p=0.001, versus p=0.30–0.96 for the tone scores). Dropping the one predictor with real evidence behind it, purely to make a formula look tidier, would have made the model worse for no real reason. It went back in before any code was written, and stayed consistent across all three model types.

## Verified after building it — every claim checked, not assumed

Running the redesigned `forecast.py` produced real, inspectable output for every model, checked line by line before trusting any of it:

- **Rate decision:** P(cut)=0.8%, P(hold)=23.7%, P(hike)=75.5%. `lag_decision_code` remained overwhelmingly the dominant predictor (coefficient 2.15, p=0.001) even after adding `wl_economy` and `wl_job_market` — both came back statistically insignificant (p=0.62, p=0.85). An honest, expected finding: the model is still mostly "meetings tend to continue the last meeting's direction," not tone.
- **Tone-forecast layer:** R² ranged 0.41–0.75 across the four topics — higher than expected going in, but economically sensible given how strongly tone persists in regime-like stretches (visible in Figure 1's redesigned chart). Predicted September values: `wl_interest_rate` 0.89 (down from July's 1.00), `wl_sentiment` 0.85 (down from 1.00), `wl_economy` −0.12, `wl_job_market` 0.58.
- **Tone momentum:** P(September more hawkish than July) = 10.6% — down from the original ceiling-distorted 20% (and the interim judgment-call override to 50–55%). This time the number comes from a real logistic regression, and it's independently corroborated by the tone-forecast layer's own prediction (both point toward mean reversion after an already-elevated reading) — though the logistic regression's own explanatory power is weak (pseudo-R²=0.09, no individually significant predictor), so it's reported as "probably meaningfully below 50%," not a precise figure.
- **Market reaction:** predicted changes remain small, P(rises) values sit in the 39–50% range across the four indicators — consistent with, not contradicted by, Table 3's mostly-insignificant tone coefficients.
- **Table 3 itself:** untouched, confirmed by design (the function reading `table3_regressions.csv` was never modified) rather than merely assumed.

## What changed in the deliverables, and what didn't

**Changed:** the rate-decision model's predictor set and output (72.7% → 75.5% hike), the tone-momentum estimate and its entire underlying method (20%/50-55% → 10%, lookup → trained model), the market-reaction forecast's tone input (July's raw numbers → a real September prediction) — visible in the notebook's forecast section, the PDF report's forecast section, and the blended final recommendation.

**Did not change:** Table 3 itself in any of its numbers, the DGS3MO-confound finding, the rate-decision classifier ([Step 12](12-figures-tables-and-decisions.md)), Figure 1, Tables 1 and 2, or the comparison-to-readings discussion.

## Documentation updated to match

`AI_USE.md` gained a second, equally direct "mistake made" entry — this one framed explicitly as a conceptual error, not a data bug, since that's a meaningfully different kind of mistake and deserves to be described as what it actually was. `PLAN.md` gained a new Section 10 recording the final design and the options rejected along the way. `README.md`'s forecast description and headline numbers were updated. `docs/steps/13-the-forecast-model.md` got correction notes left visible alongside the original (now-superseded) description, matching how Step 17 handled the minutes-date correction.

**Back to:** [the central index](../STORY.md).
