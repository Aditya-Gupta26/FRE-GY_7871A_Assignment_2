# Step 15: PDF Report Generation

The assignment's second deliverable is a standalone PDF report for Brightspace — a different artifact from the notebook, with a fixed, specified structure (Table 1, Figure 1, Table 2, Table 3, a comparison-to-readings discussion, and the forecast/recommendation).

## Choosing a tool, not just picking one

We checked what was actually available on the machine before writing anything: `pandoc` and `wkhtmltopdf` were not installed, but `weasyprint` (an HTML-to-PDF renderer) was already present as a command-line tool. That determined the approach: generate the report as clean HTML with embedded CSS, then convert it with `weasyprint report.html report.pdf` — rather than reaching for a heavier dependency (like installing LaTeX) that wasn't already there and would cost time to set up on a tight deadline.

## `src/generate_report.py`

**What it does:** builds one self-contained HTML file, pulling every table and figure live from the same data files everything else in this project reads from — `corpus.parquet` for Table 1, `table2_warsh_era.csv` for Table 2, `table3_regressions.csv` for Table 3, `forecast_market_reaction.csv` for the market-reaction forecast — and embedding Figure 1 directly into the HTML as a base64 data URI (so the report is one file with no separate image dependency to lose track of). The prose sections (methodology summary, comparison to the readings, forecast, and recommendation) are written directly into the HTML, mirroring the notebook's own narrative so the two deliverables tell a consistent story.

**Why generate it from a script rather than write the HTML by hand:** every number in the report needed to be traceable to, and automatically consistent with, the same pipeline outputs used everywhere else. Hand-copying numbers from the notebook into a separate document is exactly how a report and its underlying analysis quietly drift apart after a late change — generating both from the same source files means that can't happen.

## Two rounds of layout bugs, both caught by actually looking at the rendered output

The first PDF render technically succeeded (no errors), but looking at the actual pages revealed real problems:

1. **Tables 2 and 3 ran off the right edge of the page.** With 9–20 columns of data at a normal font size on a portrait page, there simply wasn't room. Fixed by switching those sections to landscape orientation (a `@page` CSS rule scoped to a `.landscape` wrapper div) and reducing the table font size.
2. **A row of Table 3 appeared to render as completely blank** at a page break. Before assuming this was a CSS problem, we went back to the underlying CSV and confirmed the actual data for that row (`finbert_sentiment_segmented`, Growth-Value) was complete and correct — ruling out a data bug before spending time on a layout fix for a data problem that didn't exist. It turned out to be exactly what it looked like: a wide table row splitting awkwardly across a page boundary. Fixed with `page-break-inside: avoid` on table rows and — since Table 3's one giant 20-column table was inherently going to be sparse and hard to read (each method only filling its own subset of columns, leaving the rest as dashes) — we went further and **split Table 3 into four separate, appropriately-sized tables, one per method**, which is both more readable and avoids the page-break problem entirely by making each table narrow enough to fit without splitting.

**Why checking the rendered PDF pages directly (not just "it exported without an error") mattered:** a PDF that "generates successfully" but is unreadable because its tables run off the page would have technically satisfied "produce a PDF" while failing the actual point of a report, which is that someone can read it.

## Result

`report/FOMC_Communications_Report.pdf` — six pages, every table fitting cleanly within the page (four of them in landscape), Figure 1 rendered at full width, and all required sections present: Table 1, Figure 1 (with the Warsh-era start marked), Table 2, Table 3 (four clean per-method tables), the comparison to the readings, and the forecast with recommendation. This file is **not** committed to the GitHub repository — it's the separate Brightspace deliverable, explicitly gitignored (see [Step 16](16-finalizing-and-shipping.md)) — and was instead delivered directly to you as a file.

**Next:** [Step 16 — Finalizing & Shipping](16-finalizing-and-shipping.md).
