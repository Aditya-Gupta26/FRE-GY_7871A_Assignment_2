# Step 9: Tone Scoring — FinBERT (Methods 1 & 3)

This step covers the other two tone-scoring methods from [Step 2](02-reading-the-research-papers.md): factor similarity and FinBERT sentiment. Both share one model (FinBERT), so they're implemented in one file and share one forward pass through the model per batch of sentences — no reason to load the same ~440MB model twice or run text through it twice.

## `src/tone_finbert.py`

**What it does:**

1. Loads `ProsusAI/finbert` (a BERT model fine-tuned for financial sentiment) via Hugging Face's `transformers` library, with `output_hidden_states=True` so we can pull both a classification result *and* a raw embedding vector from the same pass.
2. **Method 1 (Factor similarity):** embeds every sentence (mean-pooled last hidden layer, using the attention mask so padding tokens don't pollute the average) and computes cosine similarity to two fixed anchor sentences — `"Inflation will rise"` and `"Interest rates will rise"` — averaged across the document into `inf_score` and `rate_score`. This is the exact method from "Parsing the Fed," down to the anchor wording.
3. **Method 3 (FinBERT sentiment):** for the same sentences, reads the classification head's output, takes the softmax probability of the "positive" class, and averages it two ways — over the whole document (the baseline), and split into three equal positional segments (roughly the first, middle, and last third of the document), since the reading showed the segmented version measurably improves fit.

**Why one shared model call, not two separate scripts:** running every sentence through FinBERT twice (once for embeddings, once for sentiment) would have roughly doubled the slowest part of the pipeline for no benefit — the model produces both outputs from the same forward pass already.

## The device benchmark — a real, counterintuitive finding

Before running this against the full 1.34-million-word corpus, we checked which compute backend to use. The machine has Apple Silicon, so PyTorch's `mps` (Metal GPU) backend was available. The intuitive assumption — "GPU is faster than CPU" — turned out to be wrong *for this specific case*: a batch of 32 short sentences took **0.066 seconds on CPU** versus **0.214 seconds on MPS**. For a model this size, running batches this small, the overhead of dispatching work to the GPU and copying results back outweighs any parallelism benefit. We only found this out because we benchmarked it directly rather than assuming — and the code comment in `tone_finbert.py` documents the actual numbers so nobody re-litigates this assumption later without re-checking.

## A stuck process, diagnosed and fixed rather than just waited out

The first run was launched using the (incorrect, at the time) assumption that MPS would be faster, piped through `| tail -100` to capture output. After several minutes, the process showed almost no CPU time accumulating and no output at all. Rather than assume it was just slow and keep waiting, we:

1. Recognized that `tail -n 100` (without `-f`) buffers its *entire* input and only prints once the source process closes — meaning we'd been unable to see any progress at all, not that there was no progress. That's a real lesson about how we were capturing output, not about the underlying job.
2. Killed the stuck process, ran the CPU-vs-MPS benchmark described above, found MPS was actually the slower choice, and fixed `DEVICE` to prefer CPU.
3. Restarted the job writing directly to a log file with unbuffered output (`python -u ... > logfile.log`), so real progress was visible this time via `tqdm`'s progress bar.

**Why this is worth documenting rather than glossing over:** the fix wasn't "wait longer" — it was recognizing that our own tooling (the output-capturing method) was hiding the truth, and separately verifying a specific technical assumption (GPU is faster) instead of trusting it. Both are the kind of thing that's tempting to skip under time pressure but that would have wasted far more time if left unexamined.

## Result

The corrected run took **12 minutes 55 seconds** on CPU to process all 311 documents (many with hundreds of sentences each — minutes and press-conference transcripts are long). Output: `data/processed/scores_finbert.parquet`, with `inf_score`, `rate_score`, `finbert_sentiment`, and the three segment scores for every document. Summary statistics showed `inf_score` centered around 0.43 and `rate_score` around 0.54 with real, non-degenerate spread — not everything collapsing to the same value, which would have suggested the anchor-similarity approach wasn't discriminating between documents at all.

**Next:** [Step 10 — Event Study](10-event-study.md).
