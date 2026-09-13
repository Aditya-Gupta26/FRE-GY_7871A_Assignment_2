# Step 3: Environment & Repo Setup

With the plan in place and the methodology grounded in the actual readings, this is where we started producing files instead of just documents.

## What we needed to resolve first

You gave us the GitHub repo URL (`Aditya-Gupta26/FRE-GY_7871A_Assignment_2`, confirmed empty and public via a direct GitHub API check), said "let's finish this today," and later sent a FRED API key. Each of those unblocked a specific piece of setup.

## A real compatibility problem, caught before it cost us time

Before creating the virtual environment, we checked `python3 --version` and found **Python 3.14.7** installed via Homebrew. Rather than assume that was fine, we checked whether PyTorch (needed for FinBERT, which is central to two of our three tone-scoring methods) actually publishes a wheel for it:

```
python3.14 -m pip index versions torch   →  error, no compatible distribution
python3.13 -m pip index versions torch   →  torch 2.14.0 available
```

Python 3.13 was also installed via Homebrew. **Why this check mattered:** building the entire environment on 3.14 and only discovering PyTorch doesn't support it yet — potentially an hour or more into FinBERT-dependent work — would have meant tearing down and rebuilding the venv mid-project, on a 3-day deadline. A 30-second check avoided that entirely.

## What got built

- **`.venv`** — a Python 3.13 virtual environment, isolated from system Python.
- **`.env`** — holds the FRED API key you sent (`FRED_API_KEY=...`), read at runtime via `python-dotenv` rather than hardcoded anywhere in source. This file was created and `.gitignore`d in the same breath, before any git operations happened, specifically so the key could never accidentally end up in a commit.
- **`.gitignore`** — excludes `.env`, `data/` (all scraped documents and market data — the assignment explicitly says "no data files" in the repo), Python caches, and the venv itself.
- **`requirements.txt`** — every Python package the project would need: `requests`/`beautifulsoup4`/`lxml`/`pdfplumber` (scraping), `pandas`/`numpy`/`pyarrow` (data), `yfinance`/`fredapi` (market data), `transformers`/`torch` (FinBERT), `nltk` (sentence splitting), `statsmodels`/`scipy`/`scikit-learn` (regression/stats), `matplotlib`/`seaborn` (plotting), `jupyter` (the deliverable notebook). This list grew twice more later (`pyarrow` and `scipy` were added when we hit `ModuleNotFoundError`s partway through — noted honestly rather than pretending the list was complete on the first pass).
- **`README.md`** — setup instructions (clone, create venv, install requirements, add your own FRED key) and a description of the data sources, written so a grader or future-you could reproduce everything from scratch.
- **`AI_USE.md`** — a stub at this point, with the intention (stated explicitly in the file itself) to keep it as a running log rather than reconstruct it at the end. See [Step 16](16-finalizing-and-shipping.md) for the final version.
- **`git init`**, remote added pointing at your GitHub URL, first commit, first push.

## Why this order specifically

`.gitignore` was written *before* `git init` in practice (both were among the very first files created), so there was never a window where a `git add .` could have accidentally staged the `.env` file or a populated `data/` folder. This is a small thing, but it's the kind of ordering choice that prevents a credential leak rather than cleaning one up after the fact.

## Result

A working, isolated Python 3.13 environment; a git repository connected to your GitHub remote; a `.env` holding your FRED key safely outside version control; and a scaffold (`README.md`, `AI_USE.md`, `.gitignore`, `requirements.txt`) ready for actual project code. First commit and push happened later, bundled with the first real code (see [Step 4](04-scraping-fomc-core-documents.md)), once there was something substantive to commit.

**Next:** [Step 4 — Scraping FOMC Core Documents](04-scraping-fomc-core-documents.md).
