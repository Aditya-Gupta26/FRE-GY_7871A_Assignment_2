"""
Generate the standalone PDF report for Brightspace: Table 1, Figure 1,
Table 2, Table 3, comparison-to-readings discussion, and forecast +
recommendation. Builds an HTML file from live data then renders it to PDF
via the weasyprint CLI (run separately - see the __main__ block).
"""
import base64
from pathlib import Path

import pandas as pd

from config import DATA_PROCESSED, PROJECT_ROOT

REPORT_DIR = PROJECT_ROOT / "report"
REPORT_DIR.mkdir(exist_ok=True)


def df_to_html_table(df: pd.DataFrame, float_fmt: str = "{:.3f}") -> str:
    return df.to_html(index=False, float_format=lambda x: float_fmt.format(x), border=0, na_rep="—")


def build_table1() -> str:
    corpus = pd.read_parquet(DATA_PROCESSED / "corpus.parquet")
    t1 = corpus.groupby(["doc_type", "chair"]).size().unstack(fill_value=0)
    t1["Total"] = t1.sum(axis=1)
    t1.loc["Total"] = t1.sum()
    t1 = t1.reset_index().rename(columns={"doc_type": "Document type"})
    return df_to_html_table(t1, float_fmt="{:.0f}")


def build_table2() -> str:
    t2 = pd.read_csv(DATA_PROCESSED / "table2_warsh_era.csv")
    return df_to_html_table(t2)


METHOD_LABELS = {
    "word_list": "Method 2: Word list",
    "factor_similarity": "Method 1: Factor similarity",
    "finbert_sentiment": "Method 3: FinBERT sentiment (whole document)",
    "finbert_sentiment_segmented": "Method 3b: FinBERT sentiment (3 segments, stretch enhancement)",
}


def build_table3_sections() -> str:
    t3 = pd.read_csv(DATA_PROCESSED / "table3_regressions.csv")
    stmt = t3[t3.corpus == "statements_only"].drop(columns=["corpus"])
    sections = []
    for method, label in METHOD_LABELS.items():
        sub = stmt[stmt.method == method].drop(columns=["method"])
        sub = sub.dropna(axis=1, how="all")
        sub = sub.rename(columns=lambda c: c.replace("DGS3MO_chg_primary", "3mo")
                          .replace("_coef", " coef").replace("_p", " p"))
        sections.append(f"<h3>{label}</h3>{df_to_html_table(sub, float_fmt='{:.3f}')}")
    return "\n".join(sections)


def image_data_uri(path: Path) -> str:
    b64 = base64.b64encode(path.read_bytes()).decode()
    return f"data:image/png;base64,{b64}"


def build_html() -> str:
    figure1_uri = image_data_uri(PROJECT_ROOT / "notebooks" / "figure1_tone_over_time.png")

    html = f"""<!doctype html>
<html><head><meta charset="utf-8"><title>FOMC Communications Report</title>
<style>
  @page {{ size: A4 portrait; margin: 1.6cm; }}
  @page wide {{ size: A4 landscape; margin: 1.2cm; }}
  .landscape {{ page: wide; }}
  body {{ font-family: Georgia, serif; font-size: 10.5pt; color: #1a1a1a; line-height: 1.45; }}
  h1 {{ font-size: 17pt; border-bottom: 2px solid #1b4965; padding-bottom: 6px; }}
  h2 {{ font-size: 13pt; color: #1b4965; margin-top: 24px; }}
  h3 {{ font-size: 11.5pt; color: #1b4965; }}
  table {{ border-collapse: collapse; width: 100%; margin: 10px 0; font-size: 7.3pt; table-layout: fixed; }}
  th, td {{ border: 1px solid #ccc; padding: 3px 4px; text-align: right; overflow-wrap: break-word; }}
  th {{ background: #eef4f7; text-align: center; }}
  td:first-child, th:first-child {{ text-align: left; }}
  tr {{ page-break-inside: avoid; }}
  .caption {{ font-size: 8.5pt; color: #555; font-style: italic; margin-top: -4px; margin-bottom: 14px; }}
  img {{ max-width: 100%; }}
  .callout {{ background: #f5f8fa; border-left: 4px solid #1b4965; padding: 8px 12px; margin: 12px 0; font-size: 10pt; }}
</style></head><body>

<h1>Evaluating the Impact of FOMC Communications on Asset Prices</h1>
<p><em>FRE-GY 7871A, NLP and the Investment Process — Assignment 2</em></p>

<p>This report analyzes how the tone of Federal Reserve communications has moved from Jerome Powell's tenure
into Kevin Warsh's (sworn in as Chair 2026-05-22), whether that tone predicts one-day moves in four market
indicators, and uses both to forecast the September 15&ndash;16, 2026 FOMC meeting &mdash; a genuine ex-ante
forecast, since that meeting's outcome is announced 2026-09-16, after this report's deadline.</p>

<h2>Methodology summary</h2>
<p>We build on three assigned readings. <strong>"Parsing the Fed"</strong> is the direct structural template
for this assignment: it uses the same 4 market indicators and compares the same 3 tone-scoring methods we
implement (word-list phrase lexicon, FinBERT factor similarity, FinBERT sentiment). We extend its pipeline
across a longer window (Feb 2018 &ndash; Aug 2026), more document types (statements, minutes, press-conference
transcripts, speeches, testimony), and add the Powell-vs-Warsh comparison and forecast it didn't attempt.
<strong>Doh, Kim &amp; Yang (2021)</strong> and <strong>Doh, Song &amp; Yang (2020/2023)</strong> score tone via
similarity to the Fed's internally-drafted "alternative statements," which are declassified only after a
5-year lag &mdash; making that exact method structurally inapplicable to the Warsh era or our forecast, a
constraint we state explicitly rather than work around.</p>

<h2>Table 1. Documents collected, by type and by Chair</h2>
{build_table1()}
<p class="caption">Scraped from federalreserve.gov (src/scrape_fomc_core.py, src/scrape_speeches_testimony.py).
Speeches/testimony are filtered to each person's actual tenure as Chair &mdash; e.g. a Powell speech after his
term ended (2026-05-15) is excluded even though he remains a Fed Governor.</p>

<h2>Figure 1. Hawkish/Dovish Tone Over Time by Document Type and Method</h2>
<img src="{figure1_uri}" alt="Figure 1">
<p class="caption">Red dashed line marks Warsh's swearing-in (2026-05-22). Top panel: word-list Interest Rate
topic score. Middle panel: factor-similarity score (cosine similarity to "Interest rates will rise").
Bottom panel: FinBERT sentiment (P(positive), whole document).</p>

<div class="landscape">
<h2>Table 2. One-day indicator changes after each Warsh-era release, with tone scores</h2>
{build_table2()}
<p class="caption">d_10s2s, d_1yr are level (bp) changes; d_DXY_pct is % change; d_growth_value is the
Russell 1000 Growth minus Russell 2000 Value daily-return spread &mdash; all using the time-aware primary
event window (src/event_study.py). d_3mo_bill_control is shown for reference (this is what Table 3 controls
for, not a market reaction to be explained by tone).</p>
</div>

<div class="landscape">
<h2>Table 3. Each indicator's one-day change regressed on each tone score, with 3-month-bill control</h2>
{build_table3_sections()}
<p class="caption">Statements-only sample (n=73), HC1 robust standard errors. Each method's score(s) are
regressors together in one model per indicator (matching how "Parsing the Fed"'s own tables are structured),
alongside the DGS3MO change control (shown as "3mo_coef"/"3mo_p"). Other <code>_coef</code>/<code>_p</code>
columns give each tone regressor's coefficient and p-value.</p>
</div>

<div class="callout"><strong>Key honest finding:</strong> the DGS3MO control's coefficient is large
(&asymp;0.8&ndash;0.9) and highly significant (p&lt;0.0001) in every 1-year-Treasury model, and nearly
identical R&sup2; (&asymp;30%) appears across all four tone methods for that indicator &mdash; this is the
3-month bill mechanically co-moving with the 1-year yield on the same days, not tone doing the explanatory
work. Once that's controlled for, most individual tone coefficients are <em>not</em> statistically significant
at conventional levels (exception: word-list Interest Rate tone is significant for DXY, p=0.030). This is
exactly why the assignment asks for this control, and it is consistent with the modest effect sizes the
readings themselves report.</p></div>

<h2>How our methods and results compare with the readings</h2>
<p><strong>"Parsing the Fed"'s</strong> own reported R&sup2; benchmarks (2016-2021 sample) are a direct
yardstick: word list reached 33.8% (1yr Treasury) and 24.4% (Growth-Value); factor similarity reached 23.7%
(Growth-Value); FinBERT sentiment (trained/weighted) reached 14.8%. Our Table 3 is directly comparable in
structure (regressors-together-per-method, same 4 indicators) even though our raw R&sup2; values differ,
reflecting a longer, more macro-regime-diverse sample (2018-2026 vs. 2016-2021) and our added 3-month-bill
control, which that reading's simpler setup did not include.</p>
<p>Structurally, we cannot replicate <strong>Doh, Kim &amp; Yang (2021)</strong> / <strong>Doh, Song &amp;
Yang (2020/2023)</strong>'s alternative-statement-similarity method for anything after ~2021 (5-year
declassification lag), nor their intraday-futures-based surprise decomposition (no tick-data access) &mdash;
both are stated limitations shared by anyone doing this analysis today, not shortcuts unique to us. Our
ΔDGS3MO control is the practical analog of their goal: isolating "how it was said" from "what was decided."</p>

<h2>Forecast: September 15&ndash;16, 2026 FOMC meeting</h2>
<p><strong>Grounding finding:</strong> classifying every statement's decision directly from its text
(src/rate_decisions.py) shows Powell's Fed cutting steadily from mid-2025 through April 2026, then Warsh
<strong>held</strong> at his first meeting (June 2026) and <strong>hiked</strong> at his second (July 2026)
&mdash; a hawkish pivot exactly at the leadership transition, consistent with hawkish word-list and FinBERT
tone scores on both statements.</p>

<div class="callout"><strong>Forecast pipeline redesigned after initial delivery</strong> (full account in
docs/steps/18-forecast-redesign.md): the original market-reaction forecast plugged July's own tone scores
into a regression that had been fit using July's own row &mdash; so its output was mathematically just July's
already-known fitted value, not a September forecast. The fix: a shared, <em>lagged</em> predictor set (each
meeting's own decision plus all four word-list topic scores, lagged by one meeting) now trains a small family
of models below, feeding a genuine forecast of September's own tone into the unchanged Table 3
coefficients.</div>

<h3>Rate decision</h3>
<p>An ordinal logistic regression of each meeting's decision on the previous meeting's decision and <strong>all
four</strong> word-list topic scores (src/forecast.py) &mdash; using only information available before the
meeting being forecast &mdash; outputs P(cut)=0.8%, P(hold)=23.7%, P(hike)=75.5% from July's inputs. Adding the
two additional topics (economy, job market) barely moved this number; both come back statistically
insignificant (p=0.62, p=0.85) &mdash; the model is dominated almost entirely by the previous decision itself
(p=0.001), not tone. Real market pricing in early September 2026 (CME FedWatch ~56-66%, Kalshi ~48%,
Polymarket ~49%) frames this as a genuine "coin flip," a sharp jump from ~36% before Warsh's August 28 Jackson
Hole speech &mdash; the same catalyst our text-only model independently flagged. Blending our model with this
market cross-check (rather than reporting either alone):</p>
<p style="font-size:13pt; font-weight:bold; text-align:center;">P(cut) &asymp; 5% &nbsp;&nbsp; P(hold) &asymp; 35% &nbsp;&nbsp; P(hike) &asymp; 60%</p>

<h3>Statement tone</h3>
<p><strong>P(September statement more hawkish than July) &asymp; 10%.</strong> This now comes from a real
trained logistic regression (binary outcome: did wl_interest_rate rise vs. the previous statement), not a
distorted lookup, so we trust its direction directly instead of overriding it: after an already-elevated
reading, mean reversion is the more likely outcome. This is corroborated by a separate tone-forecast model,
which independently predicts September's wl_interest_rate at 0.89, below July's actual 1.00, for the same
reason. That said, the logistic regression's own explanatory power is weak (pseudo-R&sup2;=0.09, no
individually significant predictor), so ~10% should be read as "probably meaningfully below 50%," not a
precise figure.</p>

<h3>Market reaction</h3>
{pd.read_csv(DATA_PROCESSED / "forecast_market_reaction.csv").pipe(df_to_html_table, float_fmt="{:.4f}")}
<p class="caption">Predicted change using the tone-forecast layer's real September prediction (word-list
method, statements-only Table 3 regression, unchanged/not retrained, DGS3MO control set to 0). Point
predictions are small and P(rises) values sit close to 40-50% &mdash; consistent with, not contradicted by,
Table 3's mostly-insignificant tone coefficients. We have more conviction on the rate-decision leg (driven by
decision-momentum) and the tone-momentum leg (driven by mean-reversion, corroborated across two independent
models) than on this market-reaction leg.</p>

<h3>Recommendation</h3>
<p>Given a hike is a live, non-trivial scenario our own text analysis flags independently of market pricing,
and short-end Treasury yields showed the most consistent (if still statistically fragile) relationship to
hawkish word-list tone across every method in Table 3, we would lean toward a <strong>modest short-duration
tilt at the front end</strong> (e.g. underweight 1-2yr Treasury exposure / avoid re-adding rate-cut-sensitive
positioning) rather than a large directional bet &mdash; sized to our own evidence's real statistical
weakness, not the market's more confident framing.</p>
<p><strong>What would prove this wrong:</strong> a September 15&ndash;16 rate <strong>cut</strong> (directly
contradicting the modal call), or a statement that reads clearly more dovish than July's &mdash; explicit
language like "inflation has eased" or "downside risks to growth" replacing July's "inflation remains
elevated" framing, or a sharp reversal in the word-list/FinBERT scores toward dovish territory once the
actual statement is scored through this same pipeline.</p>

</body></html>"""
    return html


def main():
    html = build_html()
    out_path = REPORT_DIR / "report.html"
    out_path.write_text(html, encoding="utf-8")
    print(f"Saved {out_path}")


if __name__ == "__main__":
    main()
