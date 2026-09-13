"""
Method 1 (factor similarity) and Method 3 (FinBERT sentiment) tone scoring.
Both reuse the same FinBERT forward pass per batch of sentences (one model
load, one pass) for efficiency:
  - Method 1: mean-pooled last-hidden-state embedding per sentence, cosine
    similarity to two anchors ("Inflation will rise", "Interest rates will
    rise") averaged over the document -> inf_score, rate_score.
  - Method 3: softmax over the classification head -> P(positive) per
    sentence, averaged over the whole document (baseline) and by 3 equal
    positional segments (stretch enhancement, per "Parsing the Fed").
"""
import numpy as np
import pandas as pd
import torch
import torch.nn.functional as F
from transformers import AutoTokenizer, AutoModelForSequenceClassification
from tqdm import tqdm

from config import DATA_PROCESSED
from text_utils import split_sentences

MODEL_NAME = "ProsusAI/finbert"
# Benchmarked: for this model size/batch size, MPS dispatch overhead makes it
# *slower* than plain CPU (0.21s vs 0.07s for a batch of 32) - CPU wins here.
DEVICE = "cuda" if torch.cuda.is_available() else "cpu"
BATCH_SIZE = 32
MAX_LEN = 128  # FOMC sentences are well under this; speeds up batching
ANCHORS = {"inf_score": "Inflation will rise", "rate_score": "Interest rates will rise"}

print(f"Loading FinBERT on device: {DEVICE}")
tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)
model = AutoModelForSequenceClassification.from_pretrained(MODEL_NAME, output_hidden_states=True)
model.to(DEVICE)
model.eval()

POSITIVE_IDX = [k for k, v in model.config.id2label.items() if v == "positive"][0]


def embed_and_classify(sentences: list[str]) -> tuple[np.ndarray, np.ndarray]:
    """Returns (embeddings [n, hidden], p_positive [n]) for a list of sentences."""
    if not sentences:
        return np.zeros((0, model.config.hidden_size)), np.zeros((0,))
    embeddings, p_positive = [], []
    for i in range(0, len(sentences), BATCH_SIZE):
        batch = sentences[i:i + BATCH_SIZE]
        enc = tokenizer(batch, padding=True, truncation=True, max_length=MAX_LEN, return_tensors="pt").to(DEVICE)
        with torch.no_grad():
            out = model(**enc)
        logits = out.logits
        probs = F.softmax(logits, dim=-1)[:, POSITIVE_IDX].cpu().numpy()
        last_hidden = out.hidden_states[-1]  # [batch, seq, hidden]
        mask = enc["attention_mask"].unsqueeze(-1).float()
        pooled = (last_hidden * mask).sum(1) / mask.sum(1).clamp(min=1e-9)
        embeddings.append(pooled.cpu().numpy())
        p_positive.append(probs)
    return np.concatenate(embeddings), np.concatenate(p_positive)


def cosine_sim(a: np.ndarray, b: np.ndarray) -> np.ndarray:
    a_norm = a / (np.linalg.norm(a, axis=-1, keepdims=True) + 1e-9)
    b_norm = b / (np.linalg.norm(b) + 1e-9)
    return a_norm @ b_norm


def score_document(text: str, anchor_embeddings: dict[str, np.ndarray]) -> dict:
    sentences = split_sentences(text)
    if not sentences:
        return {"inf_score": np.nan, "rate_score": np.nan, "finbert_sentiment": np.nan,
                "finbert_seg1": np.nan, "finbert_seg2": np.nan, "finbert_seg3": np.nan, "n_sentences": 0}

    embeddings, p_positive = embed_and_classify(sentences)

    result = {"n_sentences": len(sentences)}
    for name, anchor_emb in anchor_embeddings.items():
        sims = cosine_sim(embeddings, anchor_emb)
        result[name] = float(np.mean(sims))

    result["finbert_sentiment"] = float(np.mean(p_positive))

    # 3 equal positional segments (stretch enhancement, per "Parsing the Fed")
    n = len(p_positive)
    thirds = np.array_split(np.arange(n), 3) if n >= 3 else [np.arange(n), np.array([]), np.array([])]
    for idx, seg in enumerate(thirds, start=1):
        result[f"finbert_seg{idx}"] = float(np.mean(p_positive[seg])) if len(seg) else np.nan

    return result


def main():
    corpus = pd.read_parquet(DATA_PROCESSED / "corpus.parquet")
    print(f"Scoring {len(corpus)} documents with FinBERT (factor similarity + sentiment)...")

    anchor_embeddings = {}
    for name, sentence in ANCHORS.items():
        emb, _ = embed_and_classify([sentence])
        anchor_embeddings[name] = emb[0]

    records = []
    for _, row in tqdm(corpus.iterrows(), total=len(corpus)):
        scores = score_document(row["text"], anchor_embeddings)
        scores["date"] = row["date"]
        scores["doc_type"] = row["doc_type"]
        records.append(scores)

    scores_df = pd.DataFrame(records)
    out_path = DATA_PROCESSED / "scores_finbert.parquet"
    scores_df.to_parquet(out_path, index=False)
    print(f"Saved to {out_path}")
    print(scores_df[["inf_score", "rate_score", "finbert_sentiment", "finbert_seg1", "finbert_seg2", "finbert_seg3"]].describe())


if __name__ == "__main__":
    main()
