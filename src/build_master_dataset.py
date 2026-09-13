"""Merge corpus metadata + all three tone-scoring outputs + event-window
market changes into one master dataframe used for Figure 1, Table 2, and
Table 3."""
import pandas as pd

from config import DATA_PROCESSED


def main():
    corpus = pd.read_parquet(DATA_PROCESSED / "corpus.parquet")
    word_list = pd.read_parquet(DATA_PROCESSED / "scores_word_list.parquet")
    finbert = pd.read_parquet(DATA_PROCESSED / "scores_finbert.parquet")
    events = pd.read_parquet(DATA_PROCESSED / "event_changes.parquet")

    meta_cols = ["date", "doc_type", "chair", "date_dt", "url", "is_special_statement",
                 "release_hour_et", "released_before_close", "n_words"]
    master = corpus[meta_cols].copy()
    master = master.merge(word_list, on=["date", "doc_type"], how="left")
    master = master.merge(finbert, on=["date", "doc_type"], how="left")
    master = master.merge(events, on=["date", "doc_type", "chair"], how="left")

    out_path = DATA_PROCESSED / "master_dataset.parquet"
    master.to_parquet(out_path, index=False)
    print(f"Saved master dataset: {master.shape} -> {out_path}")
    print(master.columns.tolist())


if __name__ == "__main__":
    main()
