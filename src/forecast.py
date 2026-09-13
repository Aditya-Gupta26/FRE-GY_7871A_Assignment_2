"""
Step 5 forecast for the September 15-16, 2026 FOMC meeting, built entirely
from Steps 2-4 (tone scores + market-reaction regressions), per PLAN.md
Section 5. Every number here is generated BEFORE the meeting's outcome is
known (it can't be known - the decision is announced 2026-09-16, after our
Sept 15 deadline), using only information available as of the last
completed communication (the July 29, 2026 statement/minutes/presconf and
the Aug 28, 2026 Jackson Hole speech).
"""
import numpy as np
import pandas as pd
from statsmodels.miscmodels.ordinal_model import OrderedModel

from config import DATA_PROCESSED

DECISION_CODE = {"cut": -1, "hold": 0, "hike": 1}


def rate_decision_probabilities() -> dict:
    decisions = pd.read_csv(DATA_PROCESSED / "rate_decisions.csv", dtype={"date": str})
    master = pd.read_parquet(DATA_PROCESSED / "master_dataset.parquet")
    stmt_tone = master[master.doc_type == "statement"][["date", "wl_interest_rate", "wl_sentiment"]]

    df = decisions.merge(stmt_tone, on="date").sort_values("date").reset_index(drop=True)
    df["decision_code"] = df["decision"].map(DECISION_CODE)
    df["lag_decision_code"] = df["decision_code"].shift(1)
    df["lag_wl_interest_rate"] = df["wl_interest_rate"].shift(1)
    df["lag_wl_sentiment"] = df["wl_sentiment"].shift(1)

    train = df.dropna(subset=["lag_decision_code", "lag_wl_interest_rate", "lag_wl_sentiment"]).copy()
    train["decision_cat"] = pd.Categorical(train["decision"], categories=["cut", "hold", "hike"], ordered=True)

    X = train[["lag_decision_code", "lag_wl_interest_rate", "lag_wl_sentiment"]]
    model = OrderedModel(train["decision_cat"], X, distr="logit")
    result = model.fit(method="bfgs", disp=False)

    # Predict the Sept 2026 meeting using the July 2026 statement (most recent
    # available before the forecast) as the "lagged" info.
    july = df[df.date == "20260729"].iloc[0]
    x_new = pd.DataFrame([{
        "lag_decision_code": july["decision_code"],
        "lag_wl_interest_rate": july["wl_interest_rate"],
        "lag_wl_sentiment": july["wl_sentiment"],
    }])
    probs = result.predict(x_new).iloc[0]
    prob_dict = {cat: probs[i] for i, cat in enumerate(["cut", "hold", "hike"])}

    return {
        "probabilities": prob_dict,
        "model_summary": result.summary(),
        "n_train": len(train),
        "unconditional_base_rate": train["decision"].value_counts(normalize=True).to_dict(),
    }


def statement_tone_momentum() -> dict:
    master = pd.read_parquet(DATA_PROCESSED / "master_dataset.parquet")
    stmt = master[master.doc_type == "statement"].sort_values("date_dt").reset_index(drop=True)
    stmt["tone_change"] = stmt["wl_interest_rate"].diff()
    stmt["increased"] = stmt["tone_change"] > 0
    stmt["prev_increased"] = stmt["increased"].shift(1)

    valid = stmt.dropna(subset=["prev_increased"])
    base_rate = valid["increased"].mean()
    conditional = valid.groupby("prev_increased")["increased"].mean()

    last_change = stmt["tone_change"].iloc[-1]  # June -> July 2026 change
    last_increased = last_change > 0
    p_more_hawkish = conditional.get(last_increased, base_rate)

    return {
        "base_rate": base_rate,
        "conditional_on_last_move": conditional.to_dict(),
        "last_move_was_increase": bool(last_increased),
        "last_two_scores": stmt[["date", "wl_interest_rate"]].tail(2).to_dict("records"),
        "p_sept_more_hawkish_than_july": p_more_hawkish,
    }


def market_reaction_forecast() -> pd.DataFrame:
    table3 = pd.read_csv(DATA_PROCESSED / "table3_regressions.csv")
    master = pd.read_parquet(DATA_PROCESSED / "master_dataset.parquet")

    wl = table3[(table3.corpus == "statements_only") & (table3.method == "word_list")].copy()
    july = master[(master.doc_type == "statement") & (master.date == "20260729")].iloc[0]
    scenario_tone = {
        "wl_interest_rate": july["wl_interest_rate"],
        "wl_economy": july["wl_economy"],
        "wl_job_market": july["wl_job_market"],
        "wl_sentiment": july["wl_sentiment"],
    }

    stmt = master[master.doc_type == "statement"]
    resid_std = {}
    for _, row in wl.iterrows():
        y_col_map = {
            "10s2s spread": "T10Y2Y_chg_primary", "1yr Treasury": "DGS1_chg_primary",
            "DXY (% chg)": "DXY_chg_primary", "Growth-Value": "GROWTH_MINUS_VALUE_chg_primary",
        }
        y_col = y_col_map[row["indicator"]]
        resid_std[row["indicator"]] = stmt[y_col].std()

    rows = []
    for _, row in wl.iterrows():
        # Predicted level of change = fitted intercept + tone terms at the "Sept looks
        # like July" scenario, with the DGS3MO control set to 0 (i.e. assuming no
        # surprise in the near-term rate path itself, isolating the pure language
        # effect - consistent with why the control is in the model at all).
        predicted = row.get("const_coef", 0) or 0
        predicted += sum((row.get(f"{k}_coef", 0) or 0) * v for k, v in scenario_tone.items())
        std = resid_std[row["indicator"]]
        from scipy.stats import norm
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

    print("\n=== Statement tone momentum ===")
    tm = statement_tone_momentum()
    print(f"  Base rate of tone increase (all history): {tm['base_rate']:.1%}")
    print(f"  Conditional on last move: {tm['conditional_on_last_move']}")
    print(f"  Last move (Jun->Jul 2026) was an increase: {tm['last_move_was_increase']}")
    print(f"  P(Sept statement more hawkish than July) = {tm['p_sept_more_hawkish_than_july']:.1%}")

    print("\n=== Market reaction forecast (word-list method, 'Sept looks like July' scenario) ===")
    mr = market_reaction_forecast()
    print(mr.to_string(index=False))

    mr.to_csv(DATA_PROCESSED / "forecast_market_reaction.csv", index=False)


if __name__ == "__main__":
    main()
