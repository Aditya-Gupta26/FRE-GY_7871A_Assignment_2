"""Sentence splitting shared by all three tone-scoring methods."""
import nltk

try:
    nltk.data.find("tokenizers/punkt_tab")
except LookupError:
    nltk.download("punkt_tab", quiet=True)

from nltk.tokenize import sent_tokenize


def split_sentences(text: str) -> list[str]:
    if not text or not text.strip():
        return []
    sentences = []
    for para in text.split("\n\n"):
        para = para.strip()
        if para:
            sentences.extend(sent_tokenize(para))
    return [s.strip() for s in sentences if len(s.strip()) > 3]


def chunk_words(words: list[str], max_len: int) -> list[list[str]]:
    return [words[i:i + max_len] for i in range(0, len(words), max_len)]
