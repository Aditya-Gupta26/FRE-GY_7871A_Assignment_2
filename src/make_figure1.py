"""
Figure 1: hawkish/dovish tone over time by document type, across all 3
tone-scoring methods, with Warsh's term start marked. Saved as a PNG for
direct inclusion in the PDF report and the notebook.
"""
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import pandas as pd

from config import DATA_PROCESSED, PROJECT_ROOT

WARSH_START = pd.Timestamp("2026-05-22")
# Distinct categorical colors (not shades of one color) so each document
# type's own trend line is easy to follow by eye. Red is deliberately
# skipped - it's reserved for the Warsh vertical line.
DOC_TYPE_COLORS = {
    "statement": "#1f77b4",  # blue
    "minutes": "#ff7f0e",    # orange
    "presconf": "#2ca02c",   # green
    "speech": "#9467bd",     # purple
    "testimony": "#8c564b",  # brown
}
DOC_TYPE_ORDER = ["statement", "minutes", "presconf", "speech", "testimony"]

PANELS = [
    ("wl_interest_rate", "Method 2: Word list (Interest Rate topic score)"),
    ("rate_score", "Method 1: Factor similarity (sim. to \"Interest rates will rise\")"),
    ("finbert_sentiment", "Method 3: FinBERT sentiment (P(positive), whole document)"),
]


def main():
    df = pd.read_parquet(DATA_PROCESSED / "master_dataset.parquet")
    df = df.sort_values("date_dt")

    fig, axes = plt.subplots(len(PANELS), 1, figsize=(12, 11), sharex=True)
    for ax, (col, title) in zip(axes, PANELS):
        for doc_type in DOC_TYPE_ORDER:
            sub = df[df.doc_type == doc_type].sort_values("date_dt")
            ax.plot(sub["date_dt"], sub[col], label=doc_type,
                     color=DOC_TYPE_COLORS[doc_type], marker="o", markersize=3,
                     linewidth=1.1, alpha=0.85)
        ax.axvline(WARSH_START, color="crimson", linestyle="--", linewidth=1.5)
        ax.set_title(title, fontsize=10, loc="left")
        ax.axhline(0.5 if col == "finbert_sentiment" else 0, color="gray", linewidth=0.6)
        ax.grid(alpha=0.25)

    axes[-1].xaxis.set_major_locator(mdates.YearLocator())
    axes[-1].xaxis.set_major_formatter(mdates.DateFormatter("%Y"))
    axes[0].legend(loc="upper left", ncol=5, fontsize=8, frameon=False)
    axes[0].text(WARSH_START, axes[0].get_ylim()[1], "  Warsh sworn in\n  (2026-05-22)",
                 fontsize=8, color="crimson", va="top")

    fig.suptitle("Figure 1. Hawkish/Dovish Tone Over Time by Document Type and Method", fontsize=13)
    fig.tight_layout()
    out_path = PROJECT_ROOT / "notebooks" / "figure1_tone_over_time.png"
    fig.savefig(out_path, dpi=150, bbox_inches="tight")
    print(f"Saved {out_path}")


if __name__ == "__main__":
    main()
