"""
Compute one-day changes in the 4 indicators (+ the DGS3MO control) around
every document's release, using two event-window versions:

  - PRIMARY (time-aware): if released before the 4pm ET close, use
    prior-trading-close -> release-day-close; if released after, use
    release-day-close -> next-trading-close.
  - SECONDARY (matches "Parsing the Fed"'s fixed convention, for direct
    comparability): prior-trading-close -> next-trading-close, regardless
    of release time.

DXY uses % change (per "Parsing the Fed"'s methodology table); T10Y2Y,
DGS1, DGS3MO use level (bp) change since they are already
spreads/yields; GROWTH_MINUS_VALUE is already a return spread (see
fetch_market_data.py) so its "change" is just its own value on the
relevant day(s), differenced the same way as a level would be, since it's
a per-day return series rather than a price level.

BUG FIX: windows are anchored on `release_date_dt`, not `date_dt`. For
every document type except minutes these are identical;
for minutes, `date_dt` is the *meeting* date while `release_date_dt` is the
true publication date (~3 weeks later, per build_corpus.py). Anchoring on
the meeting date instead - the original version of this script - silently
computed each minutes document's "market reaction" using the wrong day
(the day of that meeting's statement/press-conference, not the day the
minutes themselves became public).
"""
import numpy as np
import pandas as pd

from config import DATA_PROCESSED

LEVEL_COLS = ["T10Y2Y", "DGS1", "DGS3MO"]
PCT_COLS = ["DXY"]
RETURN_SPREAD_COLS = ["GROWTH_MINUS_VALUE"]  # already a daily return-difference series


def load_panel() -> pd.DataFrame:
    panel = pd.read_csv(DATA_PROCESSED / "market_panel.csv", index_col=0, parse_dates=True)
    panel.index = pd.to_datetime(panel.index).normalize()
    return panel


def _valid_dates(panel: pd.DataFrame, col: str) -> pd.DatetimeIndex:
    return panel.index[panel[col].notna()].sort_values()


def _on_or_after(valid: pd.DatetimeIndex, date: pd.Timestamp) -> pd.Timestamp | None:
    pos = valid.searchsorted(date, side="left")
    return valid[pos] if pos < len(valid) else None


def _strictly_before(valid: pd.DatetimeIndex, date: pd.Timestamp) -> pd.Timestamp | None:
    pos = valid.searchsorted(date, side="left")
    return valid[pos - 1] if pos > 0 else None


def _strictly_after(valid: pd.DatetimeIndex, date: pd.Timestamp) -> pd.Timestamp | None:
    pos = valid.searchsorted(date, side="right")
    return valid[pos] if pos < len(valid) else None


def compute_changes_for_column(panel: pd.DataFrame, col: str, release_date: pd.Timestamp,
                                released_before_close: bool) -> dict:
    valid = _valid_dates(panel, col)
    release_day = _on_or_after(valid, release_date)  # handles col-specific holidays
    if release_day is None:
        return {"primary": np.nan, "secondary": np.nan}

    prior_day = _strictly_before(valid, release_day)
    next_day = _strictly_after(valid, release_day)
    if prior_day is None or next_day is None:
        return {"primary": np.nan, "secondary": np.nan}

    v_prior, v_release, v_next = panel.loc[prior_day, col], panel.loc[release_day, col], panel.loc[next_day, col]

    if col in PCT_COLS:
        primary = (v_release / v_prior - 1) if released_before_close else (v_next / v_release - 1)
        secondary = v_next / v_prior - 1
    else:  # level change (yields) or already-a-return series (growth-value spread)
        primary = (v_release - v_prior) if released_before_close else (v_next - v_release)
        secondary = v_next - v_prior

    return {"primary": primary, "secondary": secondary}


def main():
    panel = load_panel()
    corpus = pd.read_parquet(DATA_PROCESSED / "corpus.parquet")

    indicator_cols = LEVEL_COLS[:2] + PCT_COLS + RETURN_SPREAD_COLS  # T10Y2Y, DGS1, DXY, GROWTH_MINUS_VALUE
    control_col = "DGS3MO"

    records = []
    for _, row in corpus.iterrows():
        # release_date_dt (not date_dt) - see build_corpus.py: for minutes,
        # date_dt is the *meeting* date, not when they were actually
        # published (~3 weeks later). release_date_dt is the corrected field.
        release_date = row["release_date_dt"].normalize()
        rec = {"date": row["date"], "doc_type": row["doc_type"], "chair": row["chair"]}
        for col in indicator_cols + [control_col]:
            changes = compute_changes_for_column(panel, col, release_date, row["released_before_close"])
            rec[f"{col}_chg_primary"] = changes["primary"]
            rec[f"{col}_chg_secondary"] = changes["secondary"]
        records.append(rec)

    out = pd.DataFrame(records)
    out_path = DATA_PROCESSED / "event_changes.parquet"
    out.to_parquet(out_path, index=False)
    print(f"Saved event-window changes for {len(out)} documents to {out_path}")
    print("\nMissing-value counts (primary window):")
    print(out[[c for c in out.columns if c.endswith("_chg_primary")]].isna().sum())


if __name__ == "__main__":
    main()
