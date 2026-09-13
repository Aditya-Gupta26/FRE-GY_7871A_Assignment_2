"""
Classify each FOMC statement's rate decision (cut/hold/hike) directly from
its text, for use in the Step 5 forecast (mapping tone -> next decision).

Approach: every statement in our 2018-2026 window uses one of exactly three
verb phrases next to "the target range for the federal funds rate":
"raise"/"raising" (hike), "lower"/"lowering" (cut), "maintain" (hold) -
verified directly against both a 2018 and a 2026 statement during scraping.
This is far more robust than parsing the numeric range text (which uses
inconsistent fraction notation, e.g. "3-1/2 to 3-3/4").
"""
import re

import pandas as pd

from config import DATA_PROCESSED

HIKE_RE = re.compile(r"\b(raise|raising)\b[^.]{0,60}target range", re.IGNORECASE)
CUT_RE = re.compile(r"\b(lower|lowering)\b[^.]{0,60}target range", re.IGNORECASE)
HOLD_RE = re.compile(r"\bmaintain\b[^.]{0,60}target range", re.IGNORECASE)


def classify_decision(text: str) -> str:
    if HIKE_RE.search(text):
        return "hike"
    if CUT_RE.search(text):
        return "cut"
    if HOLD_RE.search(text):
        return "hold"
    return "unknown"


def main():
    corpus = pd.read_parquet(DATA_PROCESSED / "corpus.parquet")
    statements = corpus[(corpus.doc_type == "statement") & (~corpus.is_special_statement)].sort_values("date_dt")

    statements = statements.copy()
    statements["decision"] = statements["text"].apply(classify_decision)

    unknown = statements[statements.decision == "unknown"]
    if len(unknown):
        print(f"WARNING: {len(unknown)} statements could not be classified:")
        print(unknown[["date"]].to_string(index=False))

    out_path = DATA_PROCESSED / "rate_decisions.csv"
    statements[["date", "chair", "decision"]].to_csv(out_path, index=False)
    print(f"\nSaved {len(statements)} classified decisions to {out_path}")
    print(statements["decision"].value_counts())
    print("\nLast 10 decisions:")
    print(statements[["date", "chair", "decision"]].tail(10).to_string(index=False))


if __name__ == "__main__":
    main()
