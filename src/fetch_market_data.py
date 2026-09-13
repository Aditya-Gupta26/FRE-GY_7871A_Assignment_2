"""
Fetch the daily market data panel needed for Tables 2 and 3:
- DXY (Yahoo DX-Y.NYB)
- Russell 1000 Growth (IWF) and Russell 2000 Value (IWN) - for Growth-Value spread
- 10s2s spread (FRED T10Y2Y), 1-year Treasury (FRED DGS1), 3-month bill (FRED DGS3MO)

Saves one combined daily panel to data/processed/market_panel.csv (gitignored -
regenerate by re-running this script).
"""
import os
from pathlib import Path

import pandas as pd
import yfinance as yf
from dotenv import load_dotenv
from fredapi import Fred

from config import DATA_PROCESSED, PROJECT_ROOT

load_dotenv(PROJECT_ROOT / ".env")

START = "2018-01-01"  # buffer before Feb 2018 so day-before-first-release changes are computable
END = "2026-09-30"    # buffer past today so late-Sept 2026 event windows are computable


def fetch_yahoo() -> pd.DataFrame:
    tickers = {"DX-Y.NYB": "DXY", "IWF": "IWF", "IWN": "IWN"}
    frames = []
    for ticker, col in tickers.items():
        df = yf.download(ticker, start=START, end=END, progress=False, auto_adjust=False)
        if df.empty:
            raise RuntimeError(f"yfinance returned no data for {ticker} - check ticker/connectivity")
        close = df["Close"].rename(columns={ticker: col}) if isinstance(df["Close"], pd.DataFrame) else df["Close"].rename(col)
        frames.append(close)
    out = pd.concat(frames, axis=1)
    out.columns = ["DXY", "IWF", "IWN"]
    return out


def fetch_fred() -> pd.DataFrame:
    api_key = os.environ.get("FRED_API_KEY")
    if not api_key:
        raise RuntimeError("FRED_API_KEY not found in environment - check .env")
    fred = Fred(api_key=api_key)
    series = {"T10Y2Y": "T10Y2Y", "DGS1": "DGS1", "DGS3MO": "DGS3MO"}
    frames = {}
    for series_id, col in series.items():
        s = fred.get_series(series_id, observation_start=START, observation_end=END)
        frames[col] = s
    out = pd.DataFrame(frames)
    out.index.name = "Date"
    return out


def main():
    print("Fetching Yahoo Finance data (DXY, IWF, IWN)...")
    yahoo_df = fetch_yahoo()
    print(f"  {len(yahoo_df)} rows")

    print("Fetching FRED data (T10Y2Y, DGS1, DGS3MO)...")
    fred_df = fetch_fred()
    print(f"  {len(fred_df)} rows")

    yahoo_df.index = pd.to_datetime(yahoo_df.index).tz_localize(None)
    fred_df.index = pd.to_datetime(fred_df.index).tz_localize(None)

    panel = yahoo_df.join(fred_df, how="outer").sort_index()

    # Growth-minus-value: difference of daily returns (per assignment spec), not price levels
    panel["IWF_ret"] = panel["IWF"].pct_change()
    panel["IWN_ret"] = panel["IWN"].pct_change()
    panel["GROWTH_MINUS_VALUE"] = panel["IWF_ret"] - panel["IWN_ret"]

    out_path = DATA_PROCESSED / "market_panel.csv"
    panel.to_csv(out_path)
    print(f"\nSaved combined panel ({len(panel)} rows, {panel.index.min()} to {panel.index.max()}) to {out_path}")
    print("\nMissing-value counts:")
    print(panel.isna().sum())


if __name__ == "__main__":
    main()
