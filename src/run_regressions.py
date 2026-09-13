"""
Table 3: regress each indicator's one-day change on each method's tone
score(s) jointly, controlling for the 3-month bill change (PLAN.md Section
3A / Section 5 Step 4). Primary corpus = statements only (matches both
readings' focus); pooled multi-type version (with doc-type dummies) is run
as our own extension beyond what either reading did.

Uses HC1 heteroskedasticity-robust standard errors throughout (a small,
explicitly-noted improvement over the readings' plain-OLS tables).
"""
import pandas as pd
import statsmodels.api as sm

from config import DATA_PROCESSED

INDICATORS = {
    "T10Y2Y_chg_primary": "10s2s spread",
    "DGS1_chg_primary": "1yr Treasury",
    "DXY_chg_primary": "DXY (% chg)",
    "GROWTH_MINUS_VALUE_chg_primary": "Growth-Value",
}
CONTROL = "DGS3MO_chg_primary"

METHOD_REGRESSORS = {
    "word_list": ["wl_interest_rate", "wl_economy", "wl_job_market", "wl_sentiment"],
    "factor_similarity": ["inf_score", "rate_score"],
    "finbert_sentiment": ["finbert_sentiment"],
    "finbert_sentiment_segmented": ["finbert_seg1", "finbert_seg2", "finbert_seg3"],
}


def run_one_regression(df: pd.DataFrame, y_col: str, x_cols: list[str]) -> dict:
    cols_needed = [y_col, CONTROL] + x_cols
    sub = df[cols_needed].dropna()
    if len(sub) < len(x_cols) + 3:
        return {"n": len(sub), "r2": None, "coefs": {}}
    X = sm.add_constant(sub[[CONTROL] + x_cols])
    y = sub[y_col]
    model = sm.OLS(y, X).fit(cov_type="HC1")
    coefs = {
        col: {"coef": model.params[col], "se": model.bse[col], "p": model.pvalues[col]}
        for col in X.columns
    }
    return {"n": len(sub), "r2": model.rsquared, "coefs": coefs}


def run_table3(df: pd.DataFrame, label: str) -> pd.DataFrame:
    rows = []
    for method, regressors in METHOD_REGRESSORS.items():
        for y_col, indicator_label in INDICATORS.items():
            result = run_one_regression(df, y_col, regressors)
            row = {"corpus": label, "method": method, "indicator": indicator_label,
                   "n": result["n"], "r2": result["r2"]}
            for reg in ["const", CONTROL] + regressors:
                c = result["coefs"].get(reg, {})
                row[f"{reg}_coef"] = c.get("coef")
                row[f"{reg}_p"] = c.get("p")
            rows.append(row)
    return pd.DataFrame(rows)


def main():
    master = pd.read_parquet(DATA_PROCESSED / "master_dataset.parquet")

    statements_only = master[master.doc_type == "statement"]
    print(f"Statements-only sample: n={len(statements_only)}")
    table3_statements = run_table3(statements_only, "statements_only")

    pooled = master[master.doc_type.isin(["statement", "minutes", "presconf"])]
    print(f"Pooled (statement+minutes+presconf) sample: n={len(pooled)}")
    table3_pooled = run_table3(pooled, "pooled_core_docs")

    out = pd.concat([table3_statements, table3_pooled], ignore_index=True)
    out_path = DATA_PROCESSED / "table3_regressions.csv"
    out.to_csv(out_path, index=False)
    print(f"\nSaved Table 3 to {out_path}\n")
    pd.set_option("display.width", 160)
    pd.set_option("display.max_columns", 20)
    print(out[out.corpus == "statements_only"][["method", "indicator", "n", "r2"]])


if __name__ == "__main__":
    main()
