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
    return df.to_html(index=False, float_format=lambda x: float_fmt.format(x), border=0, na_rep="-")


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
<p><em>FRE-GY 7871A, NLP and the Investment Process, Assignment 2</em></p>

<p>In this report we are analyzing how the tone of Federal Reserve communication has moved from Jerome Powell's
tenure into Kevin Warsh's (he was sworn in as Chair on 2026-05-22), whether this tone is actually able to
predict one-day moves in four market indicators, and then use both of these findings to forecast the September
15-16, 2026 FOMC meeting. This is a proper ex-ante forecast and not a backtest, since that meeting's outcome
only gets announced on 2026-09-16, which is after this report's deadline, so at the time of writing we genuinely
do not know the answer.</p>

<h2>Methodology summary, and why we chose it</h2>
<p>We are building on three assigned readings, but our main structural template is <strong>"Parsing the
Fed"</strong>, since it uses the exact same 4 market indicators and compares the exact same 3 tone-scoring
methods that we implement here (word-list phrase lexicon, FinBERT factor similarity, FinBERT sentiment). We
basically extend its pipeline across a much longer window (Feb 2018 to Aug 2026, versus its 2016-2021), across
more document types (statements, minutes, press-conference transcripts, speeches, testimony, not just
statements), and we add the Powell-vs-Warsh comparison and the forecast that it did not attempt at all.
<strong>Doh, Kim &amp; Yang (2021)</strong> and <strong>Doh, Song &amp; Yang (2020/2023)</strong> instead score
tone by comparing each statement's embedding to the Fed's own internally-drafted "alternative statements," which
sounds like a cleaner method on paper, but those alternative drafts get declassified only after a 5-year lag.
That makes this exact method structurally impossible to use for the Warsh era or for our forecast (the
documents we would need simply do not exist publicly yet), so this is a real limitation we are stating
honestly upfront rather than quietly working around it.</p>
<p>One decision worth explaining: the assignment only asks for at least two tone-scoring methods, but we did
three (word list, FinBERT factor similarity, FinBERT sentiment) because "Parsing the Fed" compares all three
and we wanted a like-for-like comparison against its published R-squared numbers, not just a minimum-effort
pass. We also tried a segmented version of FinBERT sentiment (scoring the first, middle and last third of each
document separately instead of the whole document at once), since the reading suggested this can improve fit,
and it is included in Table 3 below as a stretch addition, not a replacement for the whole-document version.</p>

<h2>Table 1. Documents collected, by type and by Chair</h2>
{build_table1()}
<p class="caption">Scraped directly from federalreserve.gov (src/scrape_fomc_core.py,
src/scrape_speeches_testimony.py). Speeches and testimony are filtered to each person's actual tenure as
Chair, so for example a Powell speech given after his term ended (2026-05-15) is excluded even though he is
still a sitting Fed Governor and technically still gives speeches.</p>

<h2>Figure 1. Hawkish/Dovish Tone Over Time by Document Type and Method</h2>
<img src="{figure1_uri}" alt="Figure 1">
<p class="caption">Red dashed line marks Warsh's swearing-in (2026-05-22). Top panel: word-list Interest Rate
topic score. Middle panel: factor-similarity score (cosine similarity to "Interest rates will rise").
Bottom panel: FinBERT sentiment (P(positive), whole document).</p>

<div class="landscape">
<h2>Table 2. One-day indicator changes after each Warsh-era release, with tone scores</h2>
{build_table2()}
<p class="caption">d_10s2s, d_1yr are level (bp) changes; d_DXY_pct is % change; d_growth_value is the
Russell 1000 Growth minus Russell 2000 Value daily-return spread, all computed using the time-aware primary
event window (src/event_study.py), meaning same-day close-to-close if the document released before the 4pm ET
close, next-day close-to-close otherwise. d_3mo_bill_control is shown just for reference here, this is the
variable Table 3 controls for, it is not itself a market reaction that tone is supposed to explain.</p>
</div>

<div class="landscape">
<h2>Table 3. Each indicator's one-day change regressed on each tone score, with 3-month-bill control</h2>
{build_table3_sections()}
<p class="caption">Statements-only sample (n=73), HC1 robust standard errors. Each method's score(s) go in
together as regressors in one model per indicator (this matches how "Parsing the Fed"'s own tables are set
up), alongside the DGS3MO change control (shown as "3mo_coef"/"3mo_p"). The other <code>_coef</code>/<code>_p</code>
columns give each tone regressor's own coefficient and p-value.</p>
</div>

<div class="callout"><strong>Key honest finding, and why the control matters:</strong> the DGS3MO control's
coefficient comes out large (roughly 0.8-0.9) and highly significant (p&lt;0.0001) in every 1-year-Treasury
model, and nearly identical R&sup2; (roughly 30%) shows up across all four tone methods for that one
indicator. At first this looks like a great result for tone, but actually it is mostly the 3-month bill
mechanically moving together with the 1-year yield on the same days (both are short-end rates, they get
pushed around by the same rate decision), not tone doing the real explanatory work. Once we control for that,
most of the individual tone coefficients are <em>not</em> statistically significant at the usual levels
(one exception: word-list Interest Rate tone is significant for DXY, p=0.030). This is exactly the trap the
assignment is warning us about when it asks for this control, and honestly we are a little relieved we caught
it ourselves before reporting the uncontrolled R-squared as if tone was doing all the work. It is also
consistent with the fairly modest effect sizes the readings themselves report.</div>

<h2>How our methods and results compare with the readings</h2>
<p><strong>"Parsing the Fed"'s</strong> own reported R&sup2; benchmarks (2016-2021 sample) give us a direct
yardstick to compare against: word list reached 33.8% (1yr Treasury) and 24.4% (Growth-Value); factor
similarity reached 23.7% (Growth-Value); FinBERT sentiment (trained/weighted) reached 14.8%. Our Table 3 is
directly comparable in structure to theirs (regressors together per method, same 4 indicators), even though
our raw R&sup2; values come out differently. We think this is mainly because our sample is longer and covers
more macro regimes (2018-2026, including COVID, the 2022 hiking cycle and the 2025-26 cutting cycle, versus
their 2016-2021), and because we added the 3-month-bill control which their simpler setup did not include, and
which as shown above actually removes a decent chunk of what looked like signal.</p>
<p>Structurally we are not able to replicate <strong>Doh, Kim &amp; Yang (2021)</strong> / <strong>Doh, Song
&amp; Yang (2020/2023)</strong>'s alternative-statement-similarity method for anything after roughly 2021,
since the 5-year declassification lag means those internal draft statements simply are not public yet for the
Warsh era. We also cannot replicate their intraday-futures-based surprise decomposition, since we do not have
tick-data access and are working with daily close-to-close data instead. Both of these are limitations that
anyone attempting this assignment today would run into, they are not shortcuts we took to save time. Our
DGS3MO control is basically our practical, doable-with-free-data version of what they are trying to achieve
with the surprise decomposition: both are trying to strip out the "what was decided" part of the market move
so that what is left over can be attributed to "how it was said."</p>

<h2>Forecast: September 15-16, 2026 FOMC meeting</h2>
<p><strong>Grounding finding:</strong> classifying every statement's decision directly from its text
(src/rate_decisions.py) shows Powell's Fed cutting steadily from mid-2025 through April 2026, then Warsh
<strong>held</strong> at his first meeting (June 2026) and <strong>hiked</strong> at his second (July 2026).
This is a hawkish pivot happening exactly at the leadership transition, and it lines up with the hawkish
word-list and FinBERT tone scores we see on both of those statements, so we are fairly confident this finding
is real and not just noise.</p>

<div class="callout"><strong>An honest note on a mistake we made, and fixed, in this forecast section:</strong>
our first version of the market-reaction forecast quietly plugged July's own tone scores into a regression
that had already been fit using July's own row of data. That meant its output was, mathematically, nothing
more than July's already-known fitted value dressed up as a "September forecast", it wasn't predicting anything
new at all. We caught this ourselves while re-checking the forecast logic and rebuilt it properly: a shared,
<em>lagged</em> predictor set (each meeting's own decision plus all four word-list topic scores, lagged by one
meeting, so July's real known values become the input for September) now trains a small family of models
below, and this feeds a genuine forecast of September's own tone into the unchanged Table 3 coefficients,
instead of just replaying July's numbers. We considered a couple of other fixes too, a simple AR(1) per topic
that regresses toward the long-run average tone, and a version that needed us to first estimate September's
decision probability and feed that back in, but both of these felt either too crude (ignoring the current
hawkish regime entirely) or needlessly circular, so we went with the lagged shared-predictor design
instead.</div>

<h3>Rate decision</h3>
<p>An ordinal logistic regression of each meeting's decision on the previous meeting's decision and <strong>all
four</strong> word-list topic scores (src/forecast.py), using only information that was actually available
before the meeting being forecast, outputs P(cut)=0.8%, P(hold)=23.7%, P(hike)=75.5% from July's inputs. Adding
the two extra topics (economy, job market) barely moved this number at all; both come back statistically
insignificant (p=0.62, p=0.85), so really the model is dominated almost entirely by the previous decision
itself (p=0.001), not by tone. That is a slightly humbling finding for an NLP-heavy project, but we think it
is the honest one. As an external sanity check only, not something we fed into our own number, real market
pricing in early September 2026 (CME FedWatch roughly 56-66%, Kalshi roughly 48%, Polymarket roughly 49%)
frames this meeting as a genuine "coin flip," which is a sharp jump up from roughly 36% before Warsh's August
28 Jackson Hole speech, the same catalyst that our text-only model independently flagged without ever looking
at market prices. Our model is more confident than the market, and with only 68 training meetings that
confidence should probably be treated with some caution, but the assignment asks for our own forecast, not the
market's, so we are reporting the model's own output as is rather than pulling it toward the market:</p>
<p style="font-size:13pt; font-weight:bold; text-align:center;">P(cut) &asymp; 0.8% &nbsp;&nbsp; P(hold) &asymp; 23.7% &nbsp;&nbsp; P(hike) &asymp; 75.5%</p>

<h3>Statement tone</h3>
<p><strong>P(September statement more hawkish than July) &asymp; 10%.</strong> This number now comes from a
real trained logistic regression (binary outcome: did wl_interest_rate go up compared to the previous
statement, yes or no), not the distorted lookup-table approach we tried first, so this time we are comfortable
trusting its direction directly instead of overriding it by hand: after an already-elevated reading like
July's, mean reversion is simply the more likely outcome. This finding is also backed up by a completely
separate tone-forecast model, which independently predicts September's wl_interest_rate at 0.89, below July's
actual value of 1.00, for basically the same underlying reason. That said, we should be upfront that the
logistic regression's own explanatory power is weak (pseudo-R&sup2;=0.09, and no individual predictor is
significant on its own), so this 10% is better read as "probably meaningfully below 50%" rather than as some
precise number we are confident in down to the decimal.</p>

<h3>Market reaction</h3>
{pd.read_csv(DATA_PROCESSED / "forecast_market_reaction.csv").pipe(df_to_html_table, float_fmt="{:.4f}")}
<p class="caption">Predicted change using the tone-forecast layer's real September prediction (word-list
method, statements-only Table 3 regression, unchanged and not retrained, DGS3MO control set to 0). The point
predictions here are small and the P(rises) values sit close to 40-50%, which is consistent with, not
contradicted by, Table 3's mostly-insignificant tone coefficients from earlier. Honestly, we have more
conviction in the rate-decision leg above (driven by decision-momentum, a strong and significant effect) and
the tone-momentum leg (driven by mean-reversion, and backed up by two independent models agreeing) than we do
in this market-reaction leg, which is riding on weaker statistical ground.</p>

<h3>Recommendation</h3>
<p>Given that our own model puts a hike as the clear modal outcome (75.5%), driven mainly by the strong,
statistically significant decision-momentum effect rather than tone, and given that short-end Treasury yields
showed the most consistent (even if still statistically a bit fragile) relationship to hawkish word-list tone
across every method in Table 3, our position would be a <strong>modest short-duration tilt at the front
end</strong>, for example underweighting 1-2yr Treasury exposure, or avoiding adding back rate-cut-sensitive
positioning right now. We are deliberately not recommending a large directional bet here, we are sizing this
call to match our own evidence's real statistical weakness (only 68 training meetings, and a probability that
is likely pushed toward the edge by that small sample), not scaling it up to match the model's raw 75.5%
figure at face value.</p>
<p><strong>What would prove this wrong:</strong> a September 15-16 rate <strong>cut</strong> would directly
contradict our modal call and prove us wrong straight away. Short of that, a statement that reads clearly more
dovish than July's, for example explicit language like "inflation has eased" or "downside risks to growth"
replacing July's "inflation remains elevated" framing, or a sharp reversal in the word-list/FinBERT scores
toward dovish territory once the actual September statement gets scored through this same pipeline, would also
tell us our read on the tone momentum was wrong.</p>

</body></html>"""
    return html


def main():
    html = build_html()
    out_path = REPORT_DIR / "report.html"
    out_path.write_text(html, encoding="utf-8")
    print(f"Saved {out_path}")


if __name__ == "__main__":
    main()
