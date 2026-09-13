"""Table 2: one-day changes in the 4 indicators after each Warsh-era
release, next to that release's tone scores from all 3 methods."""
import pandas as pd

from config import DATA_PROCESSED


def main():
    df = pd.read_parquet(DATA_PROCESSED / "master_dataset.parquet")
    warsh = df[df.chair == "Warsh"].sort_values("date_dt").copy()

    cols = [
        "date", "doc_type",
        "wl_interest_rate", "wl_economy", "wl_job_market", "wl_sentiment",
        "inf_score", "rate_score", "finbert_sentiment",
        "T10Y2Y_chg_primary", "DGS1_chg_primary", "DXY_chg_primary", "GROWTH_MINUS_VALUE_chg_primary",
        "DGS3MO_chg_primary",
    ]
    table2 = warsh[cols].rename(columns={
        "T10Y2Y_chg_primary": "d_10s2s", "DGS1_chg_primary": "d_1yr",
        "DXY_chg_primary": "d_DXY_pct", "GROWTH_MINUS_VALUE_chg_primary": "d_growth_value",
        "DGS3MO_chg_primary": "d_3mo_bill_control",
    })
    out_path = DATA_PROCESSED / "table2_warsh_era.csv"
    table2.to_csv(out_path, index=False)
    print(f"Saved Table 2 ({len(table2)} rows) to {out_path}\n")
    pd.set_option("display.width", 200)
    pd.set_option("display.max_columns", 20)
    print(table2.to_string(index=False))


if __name__ == "__main__":
    main()
