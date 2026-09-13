"""
Merge the two scraped document sets (FOMC core: statements/minutes/presconf,
and speeches/testimony) into one unified corpus dataframe, with a parsed
release timestamp used for the event-study window in later steps.
"""
import json
import re
from datetime import datetime, time as dtime

import pandas as pd

from config import DATA_PROCESSED

CORE_PATH = DATA_PROCESSED / "fomc_core_documents.json"
SPEECHES_PATH = DATA_PROCESSED / "speeches_testimony_documents.json"
OUT_PATH = DATA_PROCESSED / "corpus.parquet"


def parse_release_hour(doc_type: str, release_time_raw: str | None) -> float:
    """Return an approximate release hour (ET, 24h) used only to decide
    same-day vs next-day close-to-close windows (see PLAN.md Section 3).
    Statements/minutes/presconf: known/documented Fed release-time
    conventions (see scrape_fomc_core.py docstring).
    Speeches/testimony: release_time_raw is just a date (no time given on
    the page), so we conservatively assume a mid-day delivery (12:00) -
    this is a documented assumption, not a scraped fact."""
    if doc_type in ("statement",):
        if release_time_raw:
            m = re.search(r"(\d{1,2}):(\d{2})\s*([ap])\.?m", release_time_raw.lower())
            if m:
                h, mi, ap = int(m.group(1)), int(m.group(2)), m.group(3)
                if ap == "p" and h != 12:
                    h += 12
                return h + mi / 60
        return 14.0  # documented Fed convention fallback: 2:00 p.m. ET
    if doc_type == "minutes":
        return 14.0
    if doc_type == "presconf":
        return 14.5
    return 12.0  # speeches/testimony: conservative assumption, see docstring


def main():
    core = json.loads(CORE_PATH.read_text())
    speeches = json.loads(SPEECHES_PATH.read_text())

    for r in core:
        r.setdefault("is_special_statement", False)
    for r in speeches:
        r["is_special_statement"] = False

    all_docs = core + speeches
    df = pd.DataFrame(all_docs)
    df["date_dt"] = pd.to_datetime(df["date"], format="%Y%m%d")
    df["release_hour_et"] = df.apply(
        lambda r: parse_release_hour(r["doc_type"], r.get("release_time_raw")), axis=1
    )
    # Market close is 4:00pm ET (16:00) for equities/FX; treasury cash market ~3:00pm ET,
    # but we use the standard 4pm close convention for the "before/after close" split.
    df["released_before_close"] = df["release_hour_et"] < 16.0

    df = df.sort_values(["date_dt", "doc_type"]).reset_index(drop=True)
    df.to_parquet(OUT_PATH, index=False)

    print(f"Merged corpus: {len(df)} documents -> {OUT_PATH}")
    print(df.groupby(["doc_type", "chair"]).size())
    print(f"\nDate range: {df['date_dt'].min().date()} to {df['date_dt'].max().date()}")
    print(f"Total words in corpus: {df['n_words'].sum():,}")


if __name__ == "__main__":
    main()
