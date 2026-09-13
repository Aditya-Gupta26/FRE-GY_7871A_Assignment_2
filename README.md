# Evaluating the Impact of FOMC Communications on Asset Prices

FRE-GY 7871A, NLP and the Investment Process — Assignment 2.

Analyzes how the tone of Fed communications (statements, minutes, Chair speeches/testimony/press-conference transcripts) has moved from Jerome Powell's tenure into Kevin Warsh's, whether that tone predicts one-day moves in four market indicators, and uses both to forecast the September 15–16, 2026 FOMC meeting.

## Repository structure

- `notebooks/` — main analysis notebook (run top-to-bottom, output saved)
- `src/` — scraping, tone-scoring, and regression code imported by the notebook
- `PLAN.md` — the working plan for this project, including methodology decisions and rationale
- `AI_USE.md` — disclosure of how AI assistance was used
- `data/` — local only, **not committed** (see `.gitignore`); regenerate by running the notebook/scripts

## Setup

```bash
python3.13 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

Create a `.env` file in the repo root with:

```
FRED_API_KEY=your_key_here
```

(free, instant signup at https://fred.stlouisfed.org/docs/api/api_key.html)

## Data sources

- Fed statements, minutes, speeches/testimony/press-conference transcripts: federalreserve.gov
- DXY, Russell 1000 Growth (IWF), Russell 2000 Value (IWN): Yahoo Finance
- 10s2s spread (T10Y2Y), 1-year Treasury (DGS1), 3-month T-bill (DGS3MO): FRED
