"""
Step 5 forecast for the September 15-16, 2026 FOMC meeting, built entirely
from Steps 2-4 (tone scores + market-reaction regressions), per PLAN.md
Section 5. Every number here is generated BEFORE the meeting's outcome is
known (it can't be known - the decision is announced 2026-09-16, after our
Sept 15 deadline), using only information available as of the last
completed communication (the July 29, 2026 statement).

REDESIGNED (see PLAN.md Section 10 / docs/steps/18-forecast-redesign.md):
the original version of this file had two real problems, both found through
discussion, not testing:
  1. market_reaction_forecast() plugged July's own tone scores into a
     regression that was FIT USING July's row - so its output was just
     July's in-sample fitted value, not a September forecast at all.
  2. statement_tone_momentum() was a 2-bucket frequency lookup on one topic
     score, not a trained model, and was badly distorted by a ceiling
     effect (July's wl_interest_rate was already at the scale's max).

The fix: one shared, lagged predictor set - each meeting's own decision and
four word-list topic scores, LAGGED by one meeting - used to train THREE
kinds of models (only the target/y changes, per the "same x, different y"
design agreed on with the user):
  - Piece 1 (rate_decision_probabilities): y = this meeting's decision.
  - The tone-forecast layer (forecast_tone_scores): y = this meeting's own
    topic score, one OLS per topic - a genuine forecast of September's own
    tone, since x for September is July's REAL, already-known values.
  - Piece 2 (statement_tone_momentum): y = binary "was this statement more
    hawkish (wl_interest_rate) than the last one," a real logistic
    regression instead of a lookup.
Piece 3 (market_reaction_forecast) is NOT retrained - Table 3 stays exactly
as fit (contemporaneous tone -> that same day's market reaction, which is
the actual question the assignment asks Table 3 to answer). It now receives
the tone-forecast layer's REAL September prediction as its input, instead
of July's raw numbers.
"""
import numpy as np
import pandas as pd
import statsmodels.api as sm
from statsmodels.miscmodels.ordinal_model import OrderedModel
from scipy.stats import norm

from config import DATA_PROCESSED

DECISION_CODE = {"cut": -1, "hold": 0, "hike": 1}
TOPIC_COLS = ["wl_interest_rate", "wl_economy", "wl_job_market", "wl_sentiment"]
FORECAST_FROM_DATE = "20260729"  # July 2026 - most recent statement before the Sept meeting


def _build_lagged_dataset() -> tuple[pd.DataFrame, list[str]]:
    """Shared training table for every model in this file: one row per
    statement (2018-2026), with that statement's own decision + 4 topic
    scores available as y-candidates, and the PREVIOUS statement's decision
    + 4 topic scores (lag_*) as the shared x used by every model below."""
    decisions = pd.read_csv(DATA_PROCESSED / "rate_decisions.csv", dtype={"date": str})
    master = pd.read_parquet(DATA_PROCESSED / "master_dataset.parquet")
    stmt_tone = master[master.doc_type == "statement"][["date"] + TOPIC_COLS]

    df = decisions.merge(stmt_tone, on="date").sort_values("date").reset_index(drop=True)
    df["decision_code"] = df["decision"].map(DECISION_CODE)
    df["lag_decision_code"] = df["decision_code"].shift(1)
    for col in TOPIC_COLS:
        df[f"lag_{col}"] = df[col].shift(1)

    lag_cols = ["lag_decision_code"] + [f"lag_{c}" for c in TOPIC_COLS]
    return df, lag_cols


def _july_x(df: pd.DataFrame, lag_cols: list[str]) -> pd.DataFrame:
    """x row used to predict September: July's own actual decision + 4 topic
    scores, placed into the same lag_* column names every model was trained
    on. July is literally the meeting immediately before the one we're
    forecasting, so these are real, known values - not estimates."""
    july = df[df.date == FORECAST_FROM_DATE].iloc[0]
    row = {"lag_decision_code": july["decision_code"]}
    for col in TOPIC_COLS:
        row[f"lag_{col}"] = july[col]
    return pd.DataFrame([row])[lag_cols]


def rate_decision_probabilities() -> dict:
    df, lag_cols = _build_lagged_dataset()
    train = df.dropna(subset=lag_cols).copy()
    train["decision_cat"] = pd.Categorical(train["decision"], categories=["cut", "hold", "hike"], ordered=True)

    X = train[lag_cols]
    model = OrderedModel(train["decision_cat"], X, distr="logit")
    result = model.fit(method="bfgs", disp=False)

    x_new = _july_x(df, lag_cols)
    probs = result.predict(x_new).iloc[0]
    prob_dict = {cat: probs[i] for i, cat in enumerate(["cut", "hold", "hike"])}

    return {
        "probabilities": prob_dict,
        "model_summary": result.summary(),
        "n_train": len(train),
        "unconditional_base_rate": train["decision"].value_counts(normalize=True).to_dict(),
    }


def forecast_tone_scores() -> dict:
    """The new middle layer. For each of the 4 word-list topics, fits
    tone_k(t) ~ lag_decision_code + lag_wl_interest_rate + lag_wl_economy +
    lag_wl_job_market + lag_wl_sentiment via OLS on ~68 historical statement
    transitions, then predicts September's value for that topic from July's
    real, known lagged inputs. Feeds both statement_tone_momentum() and
    market_reaction_forecast() - neither of those functions fits its own
    tone model anymore, they both consume this one."""
    df, lag_cols = _build_lagged_dataset()
    train = df.dropna(subset=lag_cols).copy()
    x_new = sm.add_constant(_july_x(df, lag_cols), has_constant="add")

    results = {}
    for topic in TOPIC_COLS:
        X = sm.add_constant(train[lag_cols])
        y = train[topic]
        model = sm.OLS(y, X).fit()
        x_pred = x_new[X.columns]
        predicted = model.predict(x_pred).iloc[0]
        results[topic] = {
            "predicted_sept": predicted,
            "july_actual": df[df.date == FORECAST_FROM_DATE].iloc[0][topic],
            "residual_std": float(np.sqrt(model.mse_resid)),
            "r2": model.rsquared,
            "n_train": len(train),
            "params": model.params.to_dict(),
            "pvalues": model.pvalues.to_dict(),
        }
    return results


def statement_tone_momentum() -> dict:
    """Redesigned: a trained logistic regression on the binary outcome "was
    this statement more hawkish (by wl_interest_rate) than the previous
    one," using the same lagged x as every other model in this file -
    replacing the original 2-bucket frequency lookup, which was both a
    non-model (no real training) and distorted by a ceiling effect (July's
    wl_interest_rate already sat at the scale's maximum)."""
    df, lag_cols = _build_lagged_dataset()
    prev_tone = df["wl_interest_rate"].shift(1)
    df["increased"] = np.where(prev_tone.isna(), np.nan, (df["wl_interest_rate"] > prev_tone).astype(float))

    train = df.dropna(subset=lag_cols + ["increased"]).copy()
    X = sm.add_constant(train[lag_cols])
    y = train["increased"]
    model = sm.Logit(y, X).fit(disp=False)

    x_new = sm.add_constant(_july_x(df, lag_cols), has_constant="add")[X.columns]
    p_more_hawkish = model.predict(x_new).iloc[0]

    return {
        "p_sept_more_hawkish_than_july": p_more_hawkish,
        "model_summary": model.summary(),
        "n_train": len(train),
        "base_rate": train["increased"].mean(),
    }


def market_reaction_forecast() -> pd.DataFrame:
    """Piece 3. Table 3 (statements-only, word-list method) is NOT
    retrained here - it stays exactly as fit in run_regressions.py
    (contemporaneous tone -> that same release's market reaction, the
    question the assignment's Table 3 actually asks). What changes is the
    scenario fed into its already-fitted coefficients: the tone-forecast
    layer's real September prediction, not July's raw numbers."""
    table3 = pd.read_csv(DATA_PROCESSED / "table3_regressions.csv")
    tone_forecast = forecast_tone_scores()

    wl = table3[(table3.corpus == "statements_only") & (table3.method == "word_list")].copy()
    master = pd.read_parquet(DATA_PROCESSED / "master_dataset.parquet")
    stmt = master[master.doc_type == "statement"]

    scenario_tone = {k: v["predicted_sept"] for k, v in tone_forecast.items()}

    y_col_map = {
        "10s2s spread": "T10Y2Y_chg_primary", "1yr Treasury": "DGS1_chg_primary",
        "DXY (% chg)": "DXY_chg_primary", "Growth-Value": "GROWTH_MINUS_VALUE_chg_primary",
    }
    resid_std = {row["indicator"]: stmt[y_col_map[row["indicator"]]].std() for _, row in wl.iterrows()}

    rows = []
    for _, row in wl.iterrows():
        predicted = row.get("const_coef", 0) or 0
        predicted += sum((row.get(f"{k}_coef", 0) or 0) * v for k, v in scenario_tone.items())
        std = resid_std[row["indicator"]]
        p_rises = 1 - norm.cdf(0, loc=predicted, scale=std) if std and std > 0 else np.nan
        rows.append({"indicator": row["indicator"], "predicted_change": predicted,
                      "residual_std": std, "p_rises": p_rises})
    return pd.DataFrame(rows)


def main():
    print("=== Rate decision probabilities (Sept 15-16, 2026) ===")
    rd = rate_decision_probabilities()
    for k, v in rd["probabilities"].items():
        print(f"  P({k}) = {v:.1%}")
    print(f"  (trained on n={rd['n_train']} meetings; unconditional base rate: {rd['unconditional_base_rate']})")
    print(rd["model_summary"])

    print("\n=== Tone-forecast layer (feeds momentum + market reaction) ===")
    tf = forecast_tone_scores()
    for topic, r in tf.items():
        print(f"  {topic}: July actual={r['july_actual']:.3f}, predicted Sept={r['predicted_sept']:.3f}, "
              f"residual_std={r['residual_std']:.3f}, R2={r['r2']:.3f}, n={r['n_train']}")

    print("\n=== Statement tone momentum (logistic regression) ===")
    tm = statement_tone_momentum()
    print(f"  Historical base rate of a tone increase: {tm['base_rate']:.1%}")
    print(f"  P(Sept statement more hawkish than July) = {tm['p_sept_more_hawkish_than_july']:.1%}")
    print(tm["model_summary"])

    print("\n=== Market reaction forecast (word-list method, tone-forecast scenario) ===")
    mr = market_reaction_forecast()
    print(mr.to_string(index=False))

    mr.to_csv(DATA_PROCESSED / "forecast_market_reaction.csv", index=False)


if __name__ == "__main__":
    main()
