"""
Method 2 - Word list / phrase lexicon tone scoring (PLAN.md Section 3A).

Formula (following "Parsing the Fed"):
    x_k(t) = (1/n_k) * sum_i sign( sum_p L(p) * S(p) * 1_k(i) )
for topic k, where the inner sum runs over lexicon phrases p of topic k
present in sentence i, L(p) is phrase word-length, S(p) is phrase sentiment
(+1/-1), and the outer sum/average runs over the n_k sentences in the
document that mention topic k at all (i.e. have a nonzero inner sum).

Phrase matching is bag-of-words within a sentence (order-independent),
per the lexicon module's docstring.
"""
import re
from collections import defaultdict

import pandas as pd

from config import DATA_PROCESSED
from lexicon import LEXICON, TOPICS
from text_utils import split_sentences

WORD_RE = re.compile(r"[a-z']+")


def tokenize(text: str) -> set[str]:
    return set(WORD_RE.findall(text.lower()))


# Precompute phrase token sets once.
_PHRASES = [
    {"words": tokenize(phrase), "topic": topic, "sentiment": sentiment, "length": len(phrase.split())}
    for phrase, topic, sentiment in LEXICON
]


def score_sentence_by_topic(sentence: str) -> dict[str, int]:
    """Returns {topic: inner_sum} for a single sentence (0 for topics not mentioned)."""
    sent_words = tokenize(sentence)
    if not sent_words:
        return {}
    totals = defaultdict(int)
    for p in _PHRASES:
        if p["words"].issubset(sent_words):
            totals[p["topic"]] += p["length"] * p["sentiment"]
    return dict(totals)


def score_document(text: str) -> dict[str, float]:
    sentences = split_sentences(text)
    topic_signs = defaultdict(list)
    for sent in sentences:
        per_topic = score_sentence_by_topic(sent)
        for topic, inner_sum in per_topic.items():
            if inner_sum != 0:
                topic_signs[topic].append(1 if inner_sum > 0 else -1)

    scores = {}
    for topic in TOPICS:
        signs = topic_signs.get(topic, [])
        scores[f"wl_{topic}"] = sum(signs) / len(signs) if signs else 0.0
        scores[f"wl_{topic}_n"] = len(signs)
    return scores


def main():
    corpus = pd.read_parquet(DATA_PROCESSED / "corpus.parquet")
    print(f"Scoring {len(corpus)} documents with the word-list method...")

    records = []
    for _, row in corpus.iterrows():
        scores = score_document(row["text"])
        scores["date"] = row["date"]
        scores["doc_type"] = row["doc_type"]
        records.append(scores)

    scores_df = pd.DataFrame(records)
    out_path = DATA_PROCESSED / "scores_word_list.parquet"
    scores_df.to_parquet(out_path, index=False)
    print(f"Saved to {out_path}")
    print(scores_df[[c for c in scores_df.columns if c.startswith("wl_") and not c.endswith("_n")]].describe())


if __name__ == "__main__":
    main()
